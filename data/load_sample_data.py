"""
Step 13: Load Sample Data into Qdrant
Creates sample documents for knowledge base and customer history
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("📚 LOADING SAMPLE DATA INTO QDRANT")
print("="*80)

# ============================================================================
# SAMPLE DATA
# ============================================================================

# Knowledge Base Documents (Company Policies, FAQs)
KB_DOCUMENTS = [
    {
        "id": "kb_001",
        "title": "Return Policy",
        "content": """
        Return Policy: Customers can return unopened products within 30 days of purchase 
        for a full refund. Items must be in original condition with all packaging and accessories. 
        Refunds are processed within 5-7 business days. Shipping costs are non-refundable unless 
        the return is due to our error. For defective items, we offer replacements immediately.
        """
    },
    {
        "id": "kb_002",
        "title": "Shipping Information",
        "content": """
        Shipping Options: We offer standard shipping (5-7 days), express shipping (2-3 days), 
        and overnight shipping. Standard shipping is free for orders over $50. Tracking 
        information is provided via email. All orders are insured. We ship to most countries 
        worldwide. International orders may have customs delays.
        """
    },
    {
        "id": "kb_003",
        "title": "Product Warranty",
        "content": """
        Warranty Coverage: All electronics come with a 1-year manufacturer's warranty covering 
        defects in materials and workmanship. Warranty does not cover physical damage, water damage, 
        or normal wear. Warranty service is available through our support team or authorized 
        service centers. Extended warranty options are available for 2 or 3 years.
        """
    },
    {
        "id": "kb_004",
        "title": "Account Management",
        "content": """
        Account Features: Create an account to track orders, save preferences, and manage 
        payment methods. Password requirements: minimum 8 characters with upper/lowercase, 
        numbers, and symbols. Two-factor authentication available for security. Account 
        information can be updated anytime in settings. Contact support to delete account.
        """
    },
    {
        "id": "kb_005",
        "title": "Complaint Resolution & Escalation",
        "content": """
        Complaint Handling: We take all customer complaints seriously. Level 1: Support team 
        attempts resolution within 24 hours. Level 2: Manager review for unresolved complaints. 
        Level 3: Executive escalation for critical issues. Compensation options include discounts, 
        replacements, full refunds, or account credits depending on severity. We aim for 100% 
        customer satisfaction and will escalate repeat complaints immediately.
        """
    },
    {
        "id": "kb_006",
        "title": "Refund Status & Delays",
        "content": """
        Refund Processing: Standard refunds take 5-7 business days. Expedited refunds available 
        for complaints (1-2 business days). Check refund status in your account under 'My Returns'. 
        For delayed refunds beyond 7 days, contact support immediately. We automatically provide 
        account credit plus 10% compensation for any refund delays. Guaranteed refund or replacement.
        """
    },
    {
        "id": "kb_007",
        "title": "Product Defects & Replacements",
        "content": """
        Defective Product Replacement: If you receive a defective item, we offer immediate 
        replacement at no cost plus return shipping. Report defects within 14 days of receipt. 
        We cover replacement shipping and expedite processing. For critical defects, we may 
        offer full refund plus 20% discount on future purchase instead of replacement.
        """
    }
]

# Customer History Records (Previous Interactions)
CUSTOMER_HISTORY = [
    {
        "customer_id": "CUST_001",
        "interaction_type": "complaint",
        "text": "Complaint #1 (2025-12-01): Customer complained about slow shipping on previous order. Resolution: expedited reshipment provided."
    },
    {
        "customer_id": "CUST_001",
        "interaction_type": "purchase",
        "text": "Purchased laptop model XPS-15 on 2025-11-20. Status: delivered. Customer satisfied."
    },
    {
        "customer_id": "CUST_001",
        "interaction_type": "complaint",
        "text": "Complaint #2 (2025-12-10): Item arrived with physical damage. Requested replacement. Status: Replacement shipped, escalated to manager."
    },
    {
        "customer_id": "CUST_001",
        "interaction_type": "complaint",
        "text": "Complaint #3 (2025-12-15): Replacement also defective. Customer extremely frustrated. CRITICAL: Third complaint in 2 weeks. Escalated to executive level. Full refund + $50 credit approved."
    },
    {
        "customer_id": "CUST_002",
        "interaction_type": "inquiry",
        "text": "Asked about warranty coverage for defective phone. Explained 1-year coverage policy. Customer satisfied."
    },
    {
        "customer_id": "CUST_002",
        "interaction_type": "refund_request",
        "text": "Requested refund for unopened tablet within 30-day window. Refund approved and processed."
    },
    {
        "customer_id": "CUST_003",
        "interaction_type": "complaint",
        "text": "Complaint (2025-12-08): Charged twice for single order. Customer angry. Amount: $299.99 duplicate charge. Status: Duplicate charge refunded within 2 hours. Escalated to billing team."
    },
    {
        "customer_id": "CUST_004",
        "interaction_type": "complaint",
        "text": "Complaint (2025-12-05): Order missing items from package. Customer missing $150 worth of accessories. Status: Replacement package shipped immediately + $25 credit."
    },
    {
        "customer_id": "CUST_005",
        "interaction_type": "complaint",
        "text": "Complaint #1 (2025-12-12): Delivery delay - order 3 days late. Status: Resolved with standard apology."
    },
    {
        "customer_id": "CUST_005",
        "interaction_type": "complaint",
        "text": "Complaint #2 (2025-12-14): Item not as described in listing. Returned and refund processing. Status: Return approved, refund in progress."
    },
]

# ============================================================================
# LOAD DATA
# ============================================================================

async def load_sample_data():
    """Load sample data into Qdrant"""
    
    try:
        from rag.qdrant_manager import qdrant_manager
        from rag.embedding_manager import embedding_manager
        
        print("\n[1] Initializing managers...")
        print(f"    ✅ Qdrant Manager: {qdrant_manager}")
        print(f"    ✅ Embedding Manager: {embedding_manager}")
        
        # ========== LOAD KNOWLEDGE BASE ==========
        print("\n[2] Loading Knowledge Base documents...")
        print(f"    Documents to load: {len(KB_DOCUMENTS)}")
        
        for doc in KB_DOCUMENTS:
            try:
                # Create document object for Qdrant
                text = f"Title: {doc['title']}\n\n{doc['content']}"
                logger.info(f"Adding KB doc: {doc['id']}")
                
                # Add to knowledge base using qdrant_manager
                qdrant_manager.add_to_kb(
                    documents=[{
                        "id": doc['id'],
                        "text": text,
                        "title": doc['title']
                    }]
                )
                print(f"    ✅ {doc['title']} (ID: {doc['id']})")
                
            except Exception as e:
                print(f"    ❌ Error loading {doc['id']}: {str(e)}")
        
        print("    ✅ Knowledge Base loaded")
        
        # ========== LOAD CUSTOMER HISTORY ==========
        print("\n[3] Loading Customer History...")
        print(f"    Records to load: {len(CUSTOMER_HISTORY)}")
        
        for record in CUSTOMER_HISTORY:
            try:
                logger.info(f"Adding history for {record['customer_id']}")
                
                # Add to customer history using qdrant_manager
                qdrant_manager.add_to_history(
                    customer_id=record['customer_id'],
                    text=record['text'],
                    interaction_type=record['interaction_type']
                )
                print(f"    ✅ {record['customer_id']}: {record['interaction_type']} ({len(record['text'])} chars)")
                
            except Exception as e:
                print(f"    ❌ Error loading history for {record['customer_id']}: {str(e)}")
        
        print("    ✅ Customer History loaded")
        
        # ========== VERIFY DATA ==========
        print("\n[4] Verifying loaded data...")
        
        try:
            kb_info = qdrant_manager.get_collection_info("knowledge_base")
            print(f"    ✅ Knowledge Base:")
            print(f"       - Name: knowledge_base")
            print(f"       - Vector size: {kb_info.get('vector_size', 'N/A')}")
            print(f"       - Points count: {kb_info.get('points_count', 'N/A')}")
            
            hist_info = qdrant_manager.get_collection_info("customer_history")
            print(f"    ✅ Customer History:")
            print(f"       - Name: customer_history")
            print(f"       - Vector size: {hist_info.get('vector_size', 'N/A')}")
            print(f"       - Points count: {hist_info.get('points_count', 'N/A')}")
        except Exception as e:
            print(f"    ⚠️  Could not verify: {str(e)}")
        
        print("\n" + "="*80)
        print("✅ SAMPLE DATA LOADED SUCCESSFULLY")
        print("="*80)
        print("\n📊 Summary:")
        print(f"   • Knowledge Base: {len(KB_DOCUMENTS)} documents loaded")
        print(f"   • Customer History: {len(CUSTOMER_HISTORY)} records loaded")
        print("\n🎯 Data is now available for:")
        print("   • KB Search (retrieval_router node)")
        print("   • Customer History Context (conditional retrieval)")
        print("   • Personalized responses based on customer history")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting sample data loader...\n")
    
    success = asyncio.run(load_sample_data())
    
    sys.exit(0 if success else 1)
