import re
import os 
import json
import logging
import time
from pathlib import Path
from uuid import uuid4
from typing import Optional, List, Dict
from dataclasses import dataclass, field

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs//textbook_processor.log', mode='a')
    ]
)

@dataclass
class TextNode:
    """Represents a node in the textbook hierarchy"""
    title: str
    content : str = None
    node_type : str = 'section'
    node_id: str = field(default_factory=lambda : str(uuid4()))
    parent_id : Optional[str] = None
    children : List['TextNode'] = field(default_factory=list)
    page_number : List[int] = field(default_factory=list)
    metadata : Dict = field(default_factory= dict)
    
class TextbookProcessor:
    def __init__(self):
        self.root = None
        self.node_map: Dict[str, TextNode] = {}
    
    def extract_parse_content(self,txt_path: str) -> str:
        if not os.path.exists(txt_path):
            logging.error(f"Text file {txt_path} not found.")
            raise FileNotFoundError(f"Text file {txt_path} not found.")
        
        with open(txt_path, 'r', encoding='utf-16') as file:
            return file.read()
    
    def detect_structure(self, text: str) -> Dict:
        """Detect document structure using regex patterns"""
        structure = {
            'chapters': [],
            'sections': [],
            'subsections': []
        }
        
        # Common patterns for structure detection
        # chapter_pattern = r"Chapter\s+\d+[.:]\s*(.*?)(?=\n)"
        # section_pattern = r"(?<!\w)\d+\.\d+\s+(.*?)(?=\n)"
        # subsection_pattern = r"(?<!\w)\d+\.\d+\.\d+\s+(.*?)(?=\n)"
        
        chapter_pattern = r'\bChapter\s+\d+\:\s+.*'
        section_pattern = r'\b\d+\.\s+.*'
        subsection_pattern = r'\b\d+\.\d+\.\s+.*'
        
        # Find all matches
        structure['chapters'] = re.finditer(chapter_pattern, text, re.IGNORECASE)
        structure['sections'] = re.finditer(section_pattern, text)
        structure['subsections'] = re.finditer(subsection_pattern, text)
        
        return structure

    def create_textbook_structure(self, title: str, content: str) -> TextNode:
        """Initialize the textbook structure with content"""
        if not isinstance(content, str):
            content = str(content)
        self.root = TextNode(title=title, node_type="root", content=None)
        self.node_map[self.root.node_id] = self.root
        
        # Detect structure
        structure = self.detect_structure(content)
        
        # Process chapters
        current_chapter = None
        current_section = None
        
        # Split content into pages
        pages = content.split("[PAGE_")
        
        for page_num, page_content in enumerate(pages[1:], 1):  
            try:
                page_text = page_content.split("]\n", 1)[1] if "]\n" in page_content else page_content
                
                # Look for chapter headings
                chapter_matches = re.finditer(r"Chapter\s+\d+[.:]\s*(.*?)(?=\n)", page_text, re.IGNORECASE)
                for match in chapter_matches:
                    chapter_title = match.group(1)
                    current_chapter = self.add_node(
                        self.root.node_id,
                        f"Chapter: {chapter_title}",
                        node_type="chapter"
                    )
                    current_chapter.page_number.append(page_num)
                
                # Look for section headings if we're in a chapter
                if current_chapter:
                    section_matches = re.finditer(r"(?<!\w)\d+\.\d+\s+(.*?)(?=\n)", page_text)
                    for match in section_matches:
                        section_title = match.group(1)
                        current_section = self.add_node(
                            current_chapter.node_id,
                            f"Section: {section_title}",
                            node_type="section"
                        )
                        current_section.page_number.append(page_num)
                
                # Add content as leaf nodes
                if current_section:
                    # Split content into paragraphs
                    paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
                    for para in paragraphs:
                        if len(para) > 100:  # Only create leaf nodes for substantial paragraphs
                            curr_leaf = self.add_node(
                                current_section.node_id,
                                f"Content from page {page_num}",
                                content=para,
                                node_type="leaf",
                            )
                            curr_leaf.page_number.append(page_num)
                            
                            
            except Exception as e:
                logging.warning(f"Error processing page {page_num}: {e}")
        return self.root

    def add_node(self, parent_id: str, title: str, content: Optional[str] = None, 
                 node_type: str = "section", page_number : int = None) -> TextNode:
        """Add a new node to the hierarchy"""
        if parent_id not in self.node_map:
            logging.error(f"Parent node {parent_id} not found.")
            raise ValueError(f"Parent node {parent_id} not found")
            
        parent = self.node_map[parent_id]
        new_node = TextNode(
            title=title,
            content=content,
            node_type=node_type,
            parent_id=parent_id,
        )
        
        parent.children.append(new_node)
        self.node_map[new_node.node_id] = new_node
        return new_node

    def save_to_file(self, filename: str):
        """Save the tree structure to a JSON file"""
        def node_to_dict(node: TextNode) -> dict:
            return {
                'title': node.title,
                'content': node.content,
                'node_type': node.node_type,
                'node_id': node.node_id,
                'parent_id': node.parent_id,
                'page_number': node.page_number,
                'metadata': node.metadata,
                'children': [node_to_dict(child) for child in node.children]
            }
        try:
            with open(filename, 'w', encoding='utf-16') as f:
                json.dump(node_to_dict(self.root), f, indent=2, ensure_ascii=False)
            logging.info(f"Structure saved to {filename}.")
        except Exception as e:
            logging.error(f"Error saving to {filename}: {e}")
            raise

def process_textbooks(txt_paths: List[str], output_dir: str):
    """Process multiple textbooks and save their hierarchical structure"""
    # Initialize processor
    processor = TextbookProcessor()
    for txt_path in txt_paths:
        try:
            # Ensure the output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Extract content from text file
            logging.info(f"Processing textbook {txt_path}...")
            content = processor.extract_parse_content(txt_path)
            
            # Extract the title from the filename
            title = Path(txt_path).stem
            
            # Create structure
            logging.info(f"Building hierarchical structure for {title}...")
            processor.create_textbook_structure(title, content)
            
            # Define output path
            output_path = os.path.join(output_dir, f"{title}_structure.json")
            
            # Save structure to a file
            processor.save_to_file(output_path)
            logging.info(f"Textbook {title} processed successfully.")
        
        except Exception as e:
            logging.error(f"Failed to process {txt_path}: {e}")
            continue  # Continue processing the next textbook

# Example usage
if __name__ == "__main__":
    # List of .txt files containing extracted content
    dir_path= Path("data//extracted")
    textbooks = [os.path.join(dir_path,file) for file in os.listdir(dir_path)]
    output_directory = Path("data//processed")
    process_textbooks(textbooks, output_directory)