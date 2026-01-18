import re
from typing import List, Optional, Dict, Any
from pathlib import Path
import pdfplumber
import PyPDF2
from loguru import logger
from .base import Paper, ProcessingParameter, ExperimentalMethod, Result


class PDFProcessor:
    def __init__(self):
        self.temperature_pattern = r'(\d+\.?\d*)\s*[°º]?\s*[CcFfKk]'
        self.pressure_pattern = r'(\d+\.?\d*)\s*(Pa|MPa|GPa|bar|atm|psi|torr)'
        self.time_pattern = r'(\d+\.?\d*)\s*(s|sec|min|hour|h|day|week)'
        self.concentration_pattern = r'(\d+\.?\d*)\s*(M|mM|μM|nM|mol/L|%|wt%|vol%)'
    
    async def extract_full_text(self, pdf_path: str) -> str:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text with pdfplumber from {pdf_path}: {e}")
            
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except Exception as e2:
                logger.error(f"Error extracting text with PyPDF2 from {pdf_path}: {e2}")
                return ""
    
    async def enrich_paper(self, paper: Paper) -> Paper:
        if not paper.pdf_path or not Path(paper.pdf_path).exists():
            logger.warning(f"PDF not found for paper {paper.paper_id}")
            return paper
        
        try:
            full_text = await self.extract_full_text(paper.pdf_path)
            paper.full_text = full_text
            
            paper.processing_parameters = self._extract_processing_parameters(full_text)
            paper.materials = self._extract_materials(full_text)
            paper.equipment = self._extract_equipment(full_text)
            paper.key_findings = self._extract_key_findings(full_text)
            paper.experimental_methods = self._extract_experimental_methods(full_text)
            paper.results = self._extract_results(full_text)
            
            logger.info(f"Enriched paper {paper.paper_id} with extracted data")
            return paper
        except Exception as e:
            logger.error(f"Error enriching paper {paper.paper_id}: {e}")
            return paper
    
    def _extract_processing_parameters(self, text: str) -> List[ProcessingParameter]:
        parameters = []
        
        temp_matches = re.finditer(self.temperature_pattern, text, re.IGNORECASE)
        for match in list(temp_matches)[:10]:
            parameters.append(ProcessingParameter(
                name="temperature",
                value=match.group(1),
                unit=match.group(0).split(match.group(1))[1].strip(),
                category="thermal"
            ))
        
        pressure_matches = re.finditer(self.pressure_pattern, text, re.IGNORECASE)
        for match in list(pressure_matches)[:10]:
            parameters.append(ProcessingParameter(
                name="pressure",
                value=match.group(1),
                unit=match.group(2),
                category="mechanical"
            ))
        
        time_matches = re.finditer(self.time_pattern, text, re.IGNORECASE)
        for match in list(time_matches)[:10]:
            parameters.append(ProcessingParameter(
                name="time",
                value=match.group(1),
                unit=match.group(2),
                category="temporal"
            ))
        
        return parameters
    
    def _extract_materials(self, text: str) -> List[str]:
        materials = []
        
        material_keywords = [
            r'(?:using|with|from)\s+([A-Z][a-z]+(?:\s+[a-z]+){0,3})',
            r'([A-Z][A-Za-z0-9\-]+)\s+(?:powder|film|substrate|solution|crystal)',
            r'(?:doped with|containing)\s+([A-Z][a-z]+)',
        ]
        
        for pattern in material_keywords:
            matches = re.finditer(pattern, text)
            for match in list(matches)[:20]:
                material = match.group(1).strip()
                if len(material) > 2 and material not in materials:
                    materials.append(material)
        
        return materials[:30]
    
    def _extract_equipment(self, text: str) -> List[str]:
        equipment = []
        
        equipment_patterns = [
            r'(?:using|with)\s+(?:a|an|the)\s+([A-Z][A-Za-z\-\s]+(?:microscope|spectrometer|analyzer|furnace|reactor|pump|detector))',
            r'([A-Z][A-Za-z\-\s]+)\s+(?:model|system|instrument|device)',
        ]
        
        for pattern in equipment_patterns:
            matches = re.finditer(pattern, text)
            for match in list(matches)[:20]:
                eq = match.group(1).strip()
                if len(eq) > 3 and eq not in equipment:
                    equipment.append(eq)
        
        return equipment[:20]
    
    def _extract_key_findings(self, text: str) -> List[str]:
        findings = []
        
        sections = re.split(r'\n(?:Abstract|ABSTRACT|Results|RESULTS|Conclusion|CONCLUSION|Discussion|DISCUSSION)\n', text)
        
        for section in sections[:3]:
            sentences = re.split(r'[.!?]\s+', section)
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in ['found', 'showed', 'demonstrated', 'observed', 'achieved', 'reported']):
                    if 50 < len(sentence) < 300:
                        findings.append(sentence.strip())
                        if len(findings) >= 10:
                            return findings
        
        return findings
    
    def _extract_experimental_methods(self, text: str) -> List[ExperimentalMethod]:
        methods = []
        
        method_patterns = [
            r'(?:Methods?|Experimental|Procedure)[:\s]+([^\.]+\.)',
            r'(?:prepared|synthesized|fabricated)\s+([^\.]+\.)',
        ]
        
        for pattern in method_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in list(matches)[:5]:
                description = match.group(1).strip()
                if len(description) > 20:
                    method = ExperimentalMethod(
                        description=description,
                        equipment=self._extract_equipment(description),
                        materials=self._extract_materials(description),
                        parameters=self._extract_processing_parameters(description)
                    )
                    methods.append(method)
        
        return methods
    
    def _extract_results(self, text: str) -> List[Result]:
        results = []
        
        result_patterns = [
            r'((?:efficiency|performance|yield|rate|conductivity|resistance|transmittance)\s+(?:of|was|is)\s+[\d\.]+\s*%?)',
            r'(measured\s+[^\.]+)',
        ]
        
        for pattern in result_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in list(matches)[:10]:
                description = match.group(1).strip()
                result = Result(
                    measurement="extracted_measurement",
                    description=description
                )
                results.append(result)
        
        return results
