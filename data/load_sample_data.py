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
    }
]

# Customer History Records (Previous Interactions)
CUSTOMER_HISTORY = [
    {
        "customer_id": "CUST_001",
        "interaction_type": "complaint",
        "text": "Customer complained about slow shipping on previous order. Resolution: expedited reshipment provided."
    },
    {
        "customer_id": "CUST_001",
        "interaction_type": "purchase",
        "text": "Purchased laptop model XPS-15 on 2025-11-20. Status: delivered. Customer satisfied."
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
    }
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
