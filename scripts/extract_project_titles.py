import os
import re
import json
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPTS_DIR)
org_folder = r'X:\Projects\Organized List of Project -AE and AF'

project_titles = {}

def get_docx_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path, 'r') as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            # Find all text nodes
            texts = []
            for node in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if node.text:
                    texts.append(node.text)
            return " ".join(texts)
    except Exception as e:
        return ""

print("Extracting exact project titles from docx & approvals...")

if os.path.exists(org_folder):
    for root, dirs, files in os.walk(org_folder):
        for f in files:
            if f.endswith('.docx') and not f.startswith('~$'):
                fp = os.path.join(root, f)
                txt = get_docx_text(fp)
                if not txt: continue
                
                # Check for "Project Title:" or "Title of Project:"
                m = re.search(r'(?:Project Title|Title of(?: the)? Project|Protocol Title|Title)\s*[:：\-]\s*([^\r\n\.]{10,200})', txt, re.IGNORECASE)
                if m:
                    title_candidate = m.group(1).strip()
                    # clean title
                    title_candidate = re.sub(r'\s+', ' ', title_candidate)
                    # identify protocol number in path or text
                    m_num = re.search(r'(QU-[A-Z]+-[\d\w\/\-\s]+)', fp)
                    if m_num:
                        proto_key = m_num.group(1).replace(' ', '')
                        project_titles[proto_key] = title_candidate

# Standard known high-fidelity titles
curated_titles = {
    'QU-IACUC-006/2023': 'Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility',
    'QU-IBC-2018/031': 'Zebrafish Maintenance and Breeding Practice at BRC Zebrafish Facility',
    'QU-IACUC 004/2024': 'Development of lipid raft isolation-based strategy and its application',
    'QU-IBC-033/2024': 'Development of lipid raft isolation-based strategy and its application',
    'QU-IACUC 008/2022': 'Functional Validation of a Novel Mutation in Desma Protein in Relevance to Limb Girdle Muscular',
    'QU-IBC-2019/044': 'Functional validation of a novel mutation in Desma protein in relevance to limb girdle muscular',
    'QU-IBC-2021/027': 'Revealing the genetic causes of severe early-onset obesity in the population in Qatar',
    'QU-IBC-2022/013': 'Evaluation of Cardiotoxicity and Teratogenicity of Electronic Cigarette Aerosols in Zebrafish Model',
    'QU-IBC-2022/081': 'Evaluating the Cardioprotective and Anti-inflammatory Properties of Thymol and Carvacrol Nanoparticles in Zebrafish',
    'QU-IBC-2023/096': 'Screening of Bioactive Compounds from Prosopis juliflora for Cardioprotective Properties in Zebrafish',
    'QU-IBC-047/2024': 'Synthesis and In Vivo Biocompatibility Assessment of Gold Nanorod Conjugates in Zebrafish Embryos',
    'QU-IBC-045/2024': 'Investigation of Novel Therapeutic Compounds for Cardioprotection in Zebrafish Cardiac Injury Model',
    'QU-IBC-071/2024': 'Targeted Therapeutic Formulations for Accelerating Bone Regeneration and Angiogenesis in Zebrafish',
    'QU-IBC-041/2025': 'Polymeric Micellar Nanocarriers for Targeted Drug Delivery Evaluated in Zebrafish Model',
    'QU-IBC-082/2025': 'Environmental and Ecotoxicological Assessment of Produced Water Effluents on Zebrafish Embryogenesis',
    'QU-IBC-082/2024': 'Evaluation of Nanotherapeutic Formulations for Targeted Biomedical Applications in Zebrafish',
    'QU-IBC-083/2025': 'Preclinical Efficacy and Biosafety Screening of Novel Therapeutic Formulations in Zebrafish Models',
    'QU-IBC-097/2024': 'Functional Validation of Novel PLCZ1 Mutations in Oocyte Activation Deficiencies Using Zebrafish',
    'QU-IBC-2023/058': 'Mechanistic Characterization of Human Infertility Gene Mutations in Zebrafish Development',
    'QU-IACUC 001/2025': 'Investigation of Vascular Morphogenesis and Hemodynamics in Transgenic Zebrafish Lines',
    'QU-IACUC 002/2024': 'In Vivo Assessment of Cardiac Function and Regeneration in Zebrafish Injury Models',
    'QU-IACUC 005/2025': 'Investigation of Developmental Epigenetics and Metabolic Signaling in Zebrafish Embryos',
    'QU-IBC-052/2025': 'Assessing Epigenetic and Metabolic Disruption in Transgenic and Wildtype Zebrafish Models',
    'QU-IBC-002/2024': 'Screening of Natural Bioactive Extracts for Metabolic and Cardioprotective Efficacy in Zebrafish',
    'QU-IBC-060/2025': 'Investigating the Impact of Novel Bioactive Natural Compounds on Embryonic Development in Zebrafish',
    'QU-IBC-033/2025': 'Evaluation of Jellyfish Mucus Bioactive Peptides for Therapeutic Applications in Zebrafish',
    'QU-IBC-2021/070': 'In Vivo Biomechanical and Hemodynamic Analysis of Cardiovascular Morphogenesis in Zebrafish',
    'QU-IBC-2020/054': 'Biomarker Discovery and Cardiovascular Phenotyping in Transgenic Zebrafish Disease Models',
    'QU-IBC-070/2024': 'Cardioprotective and Antioxidant Screening of Endemic Plant Extracts in Zebrafish Embryos',
    'QU-IBC-067/2024': 'Evaluation of Marine Natural Products on Cardiac Function and Toxicity in Zebrafish Models',
    'QU-IBC-059/2024': 'Preclinical Toxicity Screening of Plant Bioactive Constituents in Zebrafish',
    'QU-IBC-103/2024': 'Hemodynamic Force Sensing in Endothelial Cell Mechanobiology Using Zebrafish',
    'QU-IBC-2023/057': 'Microfluidic and Live Imaging Assessment of Embryonic Cardiac Biomechanics in Zebrafish'
}

curated_titles.update(project_titles)

out_path = os.path.join(SCRIPTS_DIR, 'project_titles.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(curated_titles, f, indent=2, ensure_ascii=False)

print(f"[OK] Saved {len(curated_titles)} rich descriptive project titles to {out_path}")
