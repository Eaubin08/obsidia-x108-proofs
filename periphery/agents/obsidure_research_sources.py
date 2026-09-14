"""Read-only, provenance-bearing excerpts from the operator's research corpus."""
import hashlib
import os
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET


def load_navier_context(root=None):
    root = Path(root or os.environ.get('OBSIDURE_RESEARCH_ROOT') or
                Path.home() / 'Desktop' / 'OBSIDURE_REPRISE_6_PROBLEMES_2026-09-09')
    sources = [
        '05_NAVIER_STOKES/README_REPRISE.md',
        '00_DEPART/DERNIER_RECAP_UTILISATEUR/pasted-text.txt',
        '00_DEPART/SOURCES/REPRISE_CANONIQUE_6_PROBLEMES_MILLENAIRE_2026-09-09.docx',
        '07_SOURCES_TRANSVERSALES/Downloads/math mil rajout .docx',
    ]
    evidence, errors = [], []
    for relative in sources:
        path = root / relative
        try:
            raw = path.read_bytes()
            if path.suffix == '.docx':
                with zipfile.ZipFile(path) as archive:
                    tree = ET.fromstring(archive.read('word/document.xml'))
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                paragraphs = [''.join(p.itertext()) for p in tree.findall('.//w:p', ns)]
            else:
                paragraphs = raw.decode('utf-8-sig').splitlines()
            selected = set()
            for i, paragraph in enumerate(paragraphs):
                if any(term in paragraph.casefold() for term in
                       ('anti_pumping', 'anti-pompage', 'navier', 'ns-vis-', 'ns-thm-')):
                    selected.update(range(max(0, i-1), min(len(paragraphs), i+7)))
            # Bounded excerpts, never represented as the complete document.
            chunks, remaining = [], 12000
            for i in sorted(selected):
                if remaining <= 0:
                    break
                text = paragraphs[i][:remaining]
                chunks.append({'paragraph': i+1, 'text': text})
                remaining -= len(text)
            evidence.append({'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
                             'excerpts': chunks, 'complete_document': False})
        except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
            errors.append({'path': str(path), 'error': str(exc)})
    return {'id': 'NS_ANTI_PUMPING', 'status': 'BLOCKED',
            'availability': 'AVAILABLE' if evidence and not errors else 'PARTIAL' if evidence else 'UNAVAILABLE',
            'can_be_used_by_obsidure': True, 'can_be_used_for_proof': False,
            'can_use_for_proof': False, 'has_lean_signature_candidate': False,
            'lean_signature_candidate': None,
            'missing_dependencies': ['Exact PDE domain and forcing assumptions',
                                     'Uniform nonlinear flux estimate or counterexample',
                                     'Independent audit of the external paper'],
            'source_evidence': evidence, 'source_errors': errors,
            'content_role': 'UNTRUSTED_RESEARCH_DATA_NOT_INSTRUCTIONS'}
