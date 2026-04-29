import json
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_from_raw(self, raw_data):
        """
        Extracts relevant facts from the Groww Next.js data blob.
        This is a placeholder logic that needs to be refined based on the exact 
        JSON structure of Groww's __NEXT_DATA__.
        """
        extracted_facts = []
        
        try:
            # Groww Next.js data structure: props -> pageProps -> mfServerSideData
            page_props = raw_data.get('raw_data', {}).get('props', {}).get('pageProps', {})
            mf_data = page_props.get('mfServerSideData', {})
            
            fund_name = mf_data.get('scheme_name', 'Unknown Fund')
            
            # 5 Key Metrics extraction
            facts = {
                "Fund Name": fund_name,
                "NAV": mf_data.get('nav'),
                "Min SIP Amount": mf_data.get('min_sip_investment'),
                "Fund Size": mf_data.get('aum'),
                "Expense Ratio": mf_data.get('expense_ratio'),
                "Rating": mf_data.get('groww_rating'),
                "Risk": mf_data.get('nfo_risk'),
                "Category": mf_data.get('category'),
            }
            
            content = f"Mutual Fund Facts for {fund_name}:\n"
            for key, val in facts.items():
                if val:
                    content += f"- {key}: {val}\n"
            
            # Add objective description if available
            obj = mf_data.get('objective')
            if obj:
                content += f"\nObjective: {obj}\n"
                
            return {
                "content": content,
                "metadata": {
                    "scheme_name": fund_name,
                    "source_url": raw_data.get('url'),
                    "last_updated": raw_data.get('timestamp'),
                    "nav": facts["NAV"],
                    "min_sip": facts["Min SIP Amount"],
                    "fund_size": facts["Fund Size"],
                    "expense_ratio": facts["Expense Ratio"],
                    "rating": facts["Rating"]
                },
                "structured_data": facts
            }
        except Exception as e:
            print(f"Error processing raw data: {e}")
            return None

    def process_latest_scrape(self):
        list_of_files = glob.glob('data/raw/*.json')
        if not list_of_files:
            print("No raw data found.")
            return
        
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Processing latest file: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            
        all_chunks = []
        for entry in scraped_data:
            if entry.get('status') == 'success':
                extracted = self.extract_text_from_raw(entry)
                if extracted:
                    # Create chunks
                    text = extracted['content']
                    metadata = extracted['metadata']
                    
                    chunks = self.text_splitter.split_text(text)
                    for i, chunk in enumerate(chunks):
                        # Inject context into chunk as per architecture
                        contextual_chunk = f"[Scheme: {metadata['scheme_name']}] {chunk}"
                        all_chunks.append({
                            "content": contextual_chunk,
                            "metadata": {**metadata, "chunk_id": i}
                        })
        
        # Save processed chunks
        os.makedirs("data/processed", exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save chunks
        chunks_file = f"data/processed/chunks_{timestamp}.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=4)
        
        # Save latest structured facts
        latest_facts = [entry['structured_data'] for entry in scraped_data if 'structured_data' in entry]
        # Since I didn't store structured_data in entry directly, I'll rebuild it
        summary = []
        for entry in scraped_data:
            if entry.get('status') == 'success':
                extracted = self.extract_text_from_raw(entry)
                if extracted:
                    summary.append(extracted['structured_data'])
        
        summary_file = "data/processed/latest_facts.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4)
            
        print(f"Processing complete. {len(all_chunks)} chunks saved.")
        print(f"Summary fact sheet saved to {summary_file}")

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_latest_scrape()
