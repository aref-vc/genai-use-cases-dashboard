#!/usr/bin/env python3
"""
GenAI Use Cases Extractor
Extracts structured use case data from Google Cloud's GenAI HTML document
"""

import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class GenAIUseCaseExtractor:
    """Extract and structure GenAI use cases from HTML"""

    AGENT_TYPES = ['Customer Agents', 'Employee Agents', 'Creative Agents',
                   'Code Agents', 'Data Agents', 'Security Agents']

    GOOGLE_TECHNOLOGIES = [
        'Vertex AI', 'Gemini', 'Cloud Run', 'BigQuery', 'Cloud Storage',
        'Google Workspace', 'Cloud Functions', 'Google Kubernetes Engine',
        'GKE', 'Dialogflow', 'Document AI', 'Doc AI', 'AlloyDB',
        'Cloud SQL', 'Firestore', 'Compute Engine', 'NotebookLM',
        'Gemini Code Assist', 'Veo', 'Imagen', 'PaLM', 'AI Studio',
        'Cloud Scheduler', 'Cloud Tasks', 'Text to Speech', 'Speech to Text',
        'Vision AI', 'Natural Language AI', 'Translation AI', 'Recommendations AI',
        'AutoML', 'AI Platform', 'TensorFlow', 'Cloud TPU', 'AI Hypercomputer',
        'Agentspace', 'MBUX Virtual Assistant', 'Gemini 1.5 Pro', 'Gemini 2.5 Pro',
        'Gemini 2.5', 'L4 GPUs', 'A100 GPUs', 'Cloud CDN', 'Cloud Load Balancing'
    ]

    def __init__(self, html_file: str):
        """Initialize with HTML file path"""
        self.html_file = html_file
        with open(html_file, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')

        self.use_cases = []
        self.current_industry = None
        self.current_agent_type = None
        self.stats = defaultdict(int)

    def extract_metrics(self, text: str) -> Dict:
        """Extract quantitative metrics from text"""
        metrics = {
            'roi_percentage': None,
            'time_saved': None,
            'cost_reduction': None,
            'efficiency_gain': None,
            'other_metrics': []
        }

        # ROI patterns
        roi_match = re.search(r'(\d+)%\s*ROI', text, re.IGNORECASE)
        if roi_match:
            metrics['roi_percentage'] = int(roi_match.group(1))

        # Time reduction patterns
        time_patterns = [
            r'reduced.*time.*from\s+(\w+)\s+to\s+(\w+)',
            r'(\d+)%\s+(?:faster|quicker)',
            r'from\s+(\d+)\s+(?:hours|days|weeks|months)\s+to\s+(\d+)\s+(?:hours|days|weeks|months|minutes|seconds)',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['time_saved'] = match.group(0)
                break

        # Cost reduction patterns
        cost_patterns = [
            r'(\d+)%\s+(?:cost|costs)\s+(?:reduction|savings)',
            r'reduced.*costs.*by\s+(\d+)%',
            r'(\d+)%\s+(?:cheaper|lower cost)',
        ]
        for pattern in cost_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['cost_reduction'] = match.group(0)
                break

        # Efficiency patterns
        efficiency_patterns = [
            r'(\d+)%\s+(?:improvement|increase|boost|gain)',
            r'improved.*by\s+(\d+)%',
            r'(\d+)X\s+(?:improvement|faster|more efficient)',
            r'increased.*by\s+(\d+)%',
        ]
        for pattern in efficiency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['efficiency_gain'] = match.group(0)
                break

        # Extract all percentage metrics
        all_percentages = re.findall(r'(\d+)%', text)
        if all_percentages:
            metrics['other_metrics'].extend([f"{p}%" for p in all_percentages])

        # Extract X multipliers
        multipliers = re.findall(r'(\d+)X', text, re.IGNORECASE)
        if multipliers:
            metrics['other_metrics'].extend([f"{m}X" for m in multipliers])

        return metrics

    def extract_technologies(self, text: str) -> List[str]:
        """Extract mentioned Google technologies"""
        found_tech = []
        text_lower = text.lower()

        for tech in self.GOOGLE_TECHNOLOGIES:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found_tech.append(tech)

        return list(set(found_tech))  # Remove duplicates

    def extract_country(self, text: str) -> Optional[str]:
        """Extract country/region mentions"""
        countries = {
            'United States': ['U.S.', 'USA', 'United States', 'American'],
            'Germany': ['German', 'Germany'],
            'Japan': ['Japanese', 'Japan'],
            'India': ['Indian', 'India'],
            'Brazil': ['Brazilian', 'Brazil'],
            'Mexico': ['Mexican', 'Mexico'],
            'United Kingdom': ['UK', 'U.K.', 'British', 'United Kingdom'],
            'France': ['French', 'France'],
            'China': ['Chinese', 'China'],
            'Taiwan': ['Taiwanese', 'Taiwan'],
            'Colombia': ['Colombian', 'Colombia'],
            'Spain': ['Spanish', 'Spain'],
            'Norway': ['Norwegian', 'Norway'],
            'Hong Kong': ['Hong Kong'],
            'Europe': ['European', 'Europe'],
            'Global': ['global', 'worldwide', 'world'],
        }

        for country, keywords in countries.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    return country

        return None

    def categorize_application(self, text: str, agent_type: str) -> str:
        """Categorize the specific application area"""
        text_lower = text.lower()

        # Customer agent categories
        if 'customer' in agent_type.lower():
            if any(word in text_lower for word in ['chatbot', 'virtual assistant', 'conversational', 'chat']):
                return 'Virtual Assistant/Chatbot'
            elif any(word in text_lower for word in ['support', 'service', 'help']):
                return 'Customer Support'
            elif any(word in text_lower for word in ['marketing', 'campaign', 'advertising', 'ad']):
                return 'Marketing & Advertising'
            elif any(word in text_lower for word in ['sales', 'ecommerce', 'commerce']):
                return 'Sales & E-commerce'
            else:
                return 'Customer Experience'

        # Employee agent categories
        elif 'employee' in agent_type.lower():
            if any(word in text_lower for word in ['document', 'contract', 'legal', 'review']):
                return 'Document Processing'
            elif any(word in text_lower for word in ['recruit', 'hiring', 'hr', 'talent']):
                return 'HR & Recruitment'
            elif any(word in text_lower for word in ['knowledge', 'search', 'research']):
                return 'Knowledge Management'
            elif any(word in text_lower for word in ['email', 'communication', 'collaboration']):
                return 'Communication & Collaboration'
            else:
                return 'Productivity Enhancement'

        # Creative agent categories
        elif 'creative' in agent_type.lower():
            if any(word in text_lower for word in ['video', 'veo', 'image', 'imagen']):
                return 'Content Generation'
            elif any(word in text_lower for word in ['design', 'creative', 'brand']):
                return 'Design & Branding'
            else:
                return 'Creative Production'

        # Code agent categories
        elif 'code' in agent_type.lower():
            return 'Code Development'

        # Data agent categories
        elif 'data' in agent_type.lower():
            if any(word in text_lower for word in ['supply chain', 'logistics', 'distribution']):
                return 'Supply Chain & Logistics'
            elif any(word in text_lower for word in ['analytics', 'insights', 'intelligence']):
                return 'Analytics & Intelligence'
            elif any(word in text_lower for word in ['prediction', 'forecast', 'model']):
                return 'Predictive Analytics'
            else:
                return 'Data Processing'

        # Security agent categories
        elif 'security' in agent_type.lower():
            return 'Security & Compliance'

        return 'Other'

    def parse_use_case(self, li_element, index: int) -> Dict:
        """Parse a single use case from <li> element"""
        # Get all text from the list item
        paragraphs = li_element.find_all('p')
        if not paragraphs:
            return None

        # First paragraph contains company and main description
        first_p = paragraphs[0]

        # Check for new entry marker
        is_new = False
        asterisk = first_p.find('span')
        if asterisk and asterisk.get_text().strip() == '*':
            is_new = True
            asterisk.decompose()  # Remove from text

        # Extract company name
        company_tag = first_p.find('strong')
        if not company_tag:
            return None

        company_name = company_tag.get_text().strip()

        # Get full description (remove company name from beginning)
        full_text = first_p.get_text().strip()

        # Extract technologies
        technologies = self.extract_technologies(full_text)

        # Extract metrics
        metrics = self.extract_metrics(full_text)

        # Extract country
        country = self.extract_country(full_text)

        # Categorize application
        application = self.categorize_application(full_text, self.current_agent_type or '')

        # Create structured use case
        use_case = {
            'id': f'uc_{index:04d}',
            'company_name': company_name,
            'industry': self.current_industry,
            'agent_type': self.current_agent_type.replace(' Agents', '') if self.current_agent_type else None,
            'is_new_entry': is_new,
            'description': full_text,
            'use_case_summary': full_text[:200] + '...' if len(full_text) > 200 else full_text,
            'technologies': technologies,
            'google_products': technologies,  # Same as technologies for now
            'metrics': metrics,
            'country': country,
            'application_area': application,
            'raw_text': full_text
        }

        return use_case

    def find_preceding_element(self, element, tag_name):
        """Find the most recent preceding element of a given tag type"""
        # Walk backwards through previous siblings and their descendants
        current = element
        while current:
            # Check previous siblings
            prev_sibling = current.find_previous_sibling(tag_name)
            if prev_sibling:
                return prev_sibling

            # Move up to parent and continue
            current = current.parent
            if not current or current.name == 'body':
                break

        return None

    def extract_all_use_cases(self):
        """Main extraction logic - processes all <ul> elements in sequence"""
        print("🚀 Starting extraction...")

        # Find the main content div
        main_content = self.soup.find('div', {'id': 'readability-page-1'})
        if not main_content:
            print("❌ Could not find main content")
            return

        use_case_index = 1

        # Find all sections (industries) and track them
        sections = main_content.find_all('section')
        print(f"📊 Found {len(sections)} industry sections\n")

        # Find all UL elements
        all_uls = main_content.find_all('ul')
        print(f"📋 Found {len(all_uls)} total <ul> lists\n")

        # Build a position map for sections and h3s
        all_elements = []
        for section in sections:
            industry_p = section.find('p')
            if industry_p:
                all_elements.append(('section', section, industry_p.get_text().strip()))

        all_h3s = main_content.find_all('h3')
        for h3 in all_h3s:
            all_elements.append(('h3', h3, h3.get_text().strip()))

        for ul in all_uls:
            all_elements.append(('ul', ul, None))

        # Sort by document position
        all_elements.sort(key=lambda x: str(x[1].sourceline) if hasattr(x[1], 'sourceline') else '0')

        # Process in document order
        current_industry = None
        current_agent = None

        for elem_type, elem, text in all_elements:
            if elem_type == 'section':
                current_industry = text
                print(f"\n📁 {current_industry}")

            elif elem_type == 'h3':
                current_agent = text
                print(f"  🏷️  {current_agent}")

            elif elem_type == 'ul':
                # Update context
                self.current_industry = current_industry
                self.current_agent_type = current_agent

                # Process list items
                list_items = elem.find_all('li', recursive=False)
                if list_items:
                    print(f"     Processing {len(list_items)} use cases")

                    for li in list_items:
                        use_case = self.parse_use_case(li, use_case_index)
                        if use_case:
                            self.use_cases.append(use_case)
                            use_case_index += 1

                            # Update stats
                            self.stats['total_use_cases'] += 1
                            if use_case['is_new_entry']:
                                self.stats['new_entries'] += 1
                            if self.current_industry:
                                self.stats[f'industry_{self.current_industry}'] += 1

        print(f"\n✅ Extraction complete: {len(self.use_cases)} use cases found")

    def generate_metadata(self) -> Dict:
        """Generate metadata summary"""
        # Count by industry
        industries = defaultdict(int)
        agent_types = defaultdict(int)
        technologies = defaultdict(int)
        applications = defaultdict(int)
        countries = defaultdict(int)

        for uc in self.use_cases:
            if uc['industry']:
                industries[uc['industry']] += 1
            if uc['agent_type']:
                agent_types[uc['agent_type']] += 1
            if uc['application_area']:
                applications[uc['application_area']] += 1
            if uc['country']:
                countries[uc['country']] += 1

            for tech in uc['technologies']:
                technologies[tech] += 1

        return {
            'total_count': len(self.use_cases),
            'new_entries_count': sum(1 for uc in self.use_cases if uc['is_new_entry']),
            'extraction_date': datetime.now().isoformat(),
            'source_file': self.html_file,
            'source_url': 'https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders',
            'industries': dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)),
            'agent_types': dict(sorted(agent_types.items(), key=lambda x: x[1], reverse=True)),
            'technologies': dict(sorted(technologies.items(), key=lambda x: x[1], reverse=True)[:20]),  # Top 20
            'applications': dict(sorted(applications.items(), key=lambda x: x[1], reverse=True)),
            'countries': dict(sorted(countries.items(), key=lambda x: x[1], reverse=True)),
        }

    def save_to_json(self, output_file: str = 'genai_use_cases.json'):
        """Save extracted data to JSON"""
        metadata = self.generate_metadata()

        output_data = {
            'metadata': metadata,
            'use_cases': self.use_cases
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved to: {output_file}")
        print(f"📊 Statistics:")
        print(f"   Total use cases: {metadata['total_count']}")
        print(f"   New entries: {metadata['new_entries_count']}")
        print(f"   Industries: {len(metadata['industries'])}")
        print(f"   Agent types: {len(metadata['agent_types'])}")
        print(f"   Technologies: {len(metadata['technologies'])}")

        return output_file

    def save_summary(self, output_file: str = 'data_summary.json'):
        """Save summary statistics"""
        metadata = self.generate_metadata()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📈 Summary saved to: {output_file}")


def main():
    """Main execution"""
    html_file = 'Real-world gen AI use cases from the world\'s leading organizations.html'

    print("=" * 70)
    print("🤖 Google GenAI Use Cases Extractor")
    print("=" * 70)

    # Initialize extractor
    extractor = GenAIUseCaseExtractor(html_file)

    # Extract all use cases
    extractor.extract_all_use_cases()

    # Save to JSON
    extractor.save_to_json('genai_use_cases.json')
    extractor.save_summary('data_summary.json')

    print("\n" + "=" * 70)
    print("✨ Extraction complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
