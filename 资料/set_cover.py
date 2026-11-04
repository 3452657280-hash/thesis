"""Save the user's filled-in cover data before final thesis generation.
Usage: python set_cover.py --name NAME --student-id ID --supervisor TEACHER --title TITLE
"""
import argparse, json
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument('--name', required=True)
p.add_argument('--student-id', required=True)
p.add_argument('--supervisor', required=True)
p.add_argument('--title', required=True)
a = p.parse_args()
out = Path(__file__).parent / 'cover_fields.json'
out.write_text(json.dumps({'name':a.name,'student_id':a.student_id,'supervisor':a.supervisor,'supervisor_title':a.title,'college':'未来技术学院','major':'智能科学与技术'},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
