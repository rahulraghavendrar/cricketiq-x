"""
CricketIQ X - Current IPL 2025/26 Squad Classifier
Maps all 10 IPL teams with current players, roles, bowling types
Run from project root: python scripts/classify_current_squads.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
os.chdir(Path(__file__).parent.parent / "backend")

from app.db.database import SessionLocal
from app.models.models import Player

# ── Complete mapping: Cricsheet name → (team, role, bowling_type, bowling_subtype)
# Cricsheet names taken from all_ipl_players.csv full list
# Roles: batter, bowler, allrounder, wicketkeeper
# bowling_type: spin, pace, none
# bowling_subtype: leg-spin, off-spin, slow-left-arm-orthodox, left-arm-wrist-spin,
#                  fast, fast-medium, medium-fast, none

CURRENT_SQUADS = {

    # ══════════════════════════════════════════════════════════
    # 1. CHENNAI SUPER KINGS (CSK)
    # ══════════════════════════════════════════════════════════
    'RD Gaikwad':       ('CSK', 'batter',       'none',  'none'),
    'D Brevis':         ('CSK', 'batter',       'none',  'none'),
    'A Mhatre':         ('CSK', 'batter',       'none',  'none'),
    'MS Dhoni':         ('CSK', 'wicketkeeper', 'none',  'none'),
    'SV Samson':        ('CSK', 'wicketkeeper', 'none',  'none'),  # Sanju Samson
    'Urvil Patel':      ('CSK', 'wicketkeeper', 'none',  'none'),
    'Kartik Sharma':    ('CSK', 'wicketkeeper', 'none',  'none'),
    'S Dube':           ('CSK', 'allrounder',   'pace',  'fast-medium'),
    'MW Short':         ('CSK', 'allrounder',   'spin',  'off-spin'),
    'PR Veer':          ('CSK', 'allrounder',   'pace',  'fast-medium'),
    'Aman Hakim Khan':  ('CSK', 'allrounder',   'pace',  'fast-medium'),
    'Noor Ahmad':       ('CSK', 'bowler',        'spin',  'left-arm-wrist-spin'),
    'RD Chahar':        ('CSK', 'bowler',        'spin',  'leg-spin'),
    'KK Ahmed':         ('CSK', 'bowler',        'pace',  'fast-medium'),
    'A Kamboj':         ('CSK', 'bowler',        'pace',  'fast-medium'),
    'MD Choudhary':     ('CSK', 'bowler',        'pace',  'fast-medium'),
    'S Gopal':          ('CSK', 'bowler',        'spin',  'leg-spin'),
    'Gurjapneet Singh': ('CSK', 'bowler',        'pace',  'fast-medium'),
    'Akash Madhwal':    ('CSK', 'bowler',        'pace',  'fast-medium'),
    'MJ Henry':         ('CSK', 'bowler',        'pace',  'fast-medium'),
    'AJ Hosein':        ('CSK', 'bowler',        'spin',  'slow-left-arm-orthodox'),

    # ══════════════════════════════════════════════════════════
    # 2. MUMBAI INDIANS (MI)
    # ══════════════════════════════════════════════════════════
    'RG Sharma':        ('MI',  'allrounder',   'spin',  'off-spin'),
    'SA Yadav':         ('MI',  'batter',       'none',  'none'),
    'Tilak Varma':      ('MI',  'batter',       'none',  'none'),
    'SE Rutherford':    ('MI',  'batter',       'none',  'none'),
    'DV Malewar':       ('MI',  'batter',       'none',  'none'),
    'Q de Kock':        ('MI',  'wicketkeeper', 'none',  'none'),
    'RD Rickelton':     ('MI',  'wicketkeeper', 'none',  'none'),
    'R Minz':           ('MI',  'wicketkeeper', 'none',  'none'),
    'HH Pandya':        ('MI',  'allrounder',   'pace',  'fast-medium'),
    'WG Jacks':         ('MI',  'allrounder',   'spin',  'off-spin'),
    'MJ Santner':       ('MI',  'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'Naman Dhir':       ('MI',  'allrounder',   'spin',  'off-spin'),
    'SN Thakur':        ('MI',  'allrounder',   'pace',  'fast-medium'),
    'RA Bawa':          ('MI',  'allrounder',   'pace',  'fast-medium'),
    'Mayank Rawat':     ('MI',  'allrounder',   'pace',  'fast-medium'),
    'C Bosch':          ('MI',  'allrounder',   'pace',  'fast-medium'),
    'JJ Bumrah':        ('MI',  'bowler',        'pace',  'fast'),
    'TA Boult':         ('MI',  'bowler',        'pace',  'fast-medium'),
    'DL Chahar':        ('MI',  'bowler',        'pace',  'medium-fast'),
    'M Markande':       ('MI',  'bowler',        'spin',  'leg-spin'),
    'AM Ghazanfar':     ('MI',  'bowler',        'spin',  'off-spin'),
    'Ashwani Kumar':    ('MI',  'bowler',        'pace',  'fast-medium'),
    'Raghu Sharma':     ('MI',  'bowler',        'spin',  'leg-spin'),

    # ══════════════════════════════════════════════════════════
    # 3. ROYAL CHALLENGERS BENGALURU (RCB)
    # ══════════════════════════════════════════════════════════
    'RM Patidar':       ('RCB', 'batter',       'none',  'none'),
    'V Kohli':          ('RCB', 'allrounder',   'spin',  'off-spin'),
    'D Padikkal':       ('RCB', 'batter',       'none',  'none'),
    'PD Salt':          ('RCB', 'wicketkeeper', 'none',  'none'),
    'JM Sharma':        ('RCB', 'wicketkeeper', 'none',  'none'),
    'KH Pandya':        ('RCB', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'VR Iyer':          ('RCB', 'allrounder',   'spin',  'off-spin'),
    'TH David':         ('RCB', 'allrounder',   'pace',  'fast-medium'),
    'R Shepherd':       ('RCB', 'allrounder',   'pace',  'fast-medium'),
    'JG Bethell':       ('RCB', 'allrounder',   'spin',  'off-spin'),
    'Swapnil Singh':    ('RCB', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'JR Hazlewood':     ('RCB', 'bowler',        'pace',  'fast-medium'),
    'B Kumar':          ('RCB', 'bowler',        'pace',  'fast-medium'),
    'Yash Dayal':       ('RCB', 'bowler',        'pace',  'fast-medium'),
    'Rasikh Salam':     ('RCB', 'bowler',        'pace',  'fast-medium'),
    'Suyash Sharma':    ('RCB', 'bowler',        'spin',  'leg-spin'),
    'N Thushara':       ('RCB', 'bowler',        'pace',  'fast-medium'),
    'JA Duffy':         ('RCB', 'bowler',        'pace',  'fast-medium'),
    'RJ Gleeson':       ('RCB', 'bowler',        'pace',  'fast-medium'),

    # ══════════════════════════════════════════════════════════
    # 4. KOLKATA KNIGHT RIDERS (KKR)
    # ══════════════════════════════════════════════════════════
    'AM Rahane':        ('KKR', 'batter',       'none',  'none'),
    'RK Singh':         ('KKR', 'batter',       'none',  'none'),
    'A Raghuvanshi':    ('KKR', 'batter',       'none',  'none'),
    'MK Pandey':        ('KKR', 'batter',       'none',  'none'),
    'RA Tripathi':      ('KKR', 'batter',       'none',  'none'),
    'R Powell':         ('KKR', 'batter',       'none',  'none'),
    'TL Seifert':       ('KKR', 'wicketkeeper', 'none',  'none'),
    'SP Narine':        ('KKR', 'allrounder',   'spin',  'off-spin'),
    'C Green':          ('KKR', 'allrounder',   'pace',  'fast-medium'),
    'R Ravindra':       ('KKR', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'Ramandeep Singh':  ('KKR', 'allrounder',   'pace',  'fast-medium'),
    'CV Varun':         ('KKR', 'bowler',        'spin',  'off-spin'),
    'M Pathirana':      ('KKR', 'bowler',        'pace',  'fast'),
    'VG Arora':         ('KKR', 'bowler',        'pace',  'fast-medium'),
    'Kartik Tyagi':     ('KKR', 'bowler',        'pace',  'fast-medium'),
    'Umran Malik':      ('KKR', 'bowler',        'pace',  'fast'),
    'Navdeep Saini':    ('KKR', 'bowler',        'pace',  'fast-medium'),
    'B Muzarabani':     ('KKR', 'bowler',        'pace',  'fast'),
    'Harshit Rana':     ('KKR', 'bowler',        'pace',  'fast-medium'),
    'SB Dubey':         ('KKR', 'bowler',        'spin',  'off-spin'),

    # ══════════════════════════════════════════════════════════
    # 5. SUNRISERS HYDERABAD (SRH)
    # ══════════════════════════════════════════════════════════
    'TM Head':          ('SRH', 'batter',       'none',  'none'),
    'Abhishek Sharma':  ('SRH', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'H Klaasen':        ('SRH', 'wicketkeeper', 'none',  'none'),
    'Nithish Kumar Reddy': ('SRH', 'allrounder','pace',  'fast-medium'),
    'Shahbaz Ahmed':    ('SRH', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'Sanvir Singh':     ('SRH', 'allrounder',   'pace',  'fast-medium'),
    'V Shankar':        ('SRH', 'allrounder',   'pace',  'fast-medium'),
    'PJ Cummins':       ('SRH', 'allrounder',   'pace',  'fast'),
    'T Natarajan':      ('SRH', 'bowler',        'pace',  'fast-medium'),
    'JD Unadkat':       ('SRH', 'bowler',        'pace',  'fast-medium'),
    'Shivam Mavi':      ('SRH', 'bowler',        'pace',  'fast-medium'),
    'Zeeshan Ansari':   ('SRH', 'bowler',        'spin',  'slow-left-arm-orthodox'),
    'E Malinga':        ('SRH', 'bowler',        'pace',  'fast-medium'),
    'Sakib Hussain':    ('SRH', 'bowler',        'pace',  'fast-medium'),
    'PP Hinge':         ('SRH', 'bowler',        'pace',  'fast-medium'),

    # ══════════════════════════════════════════════════════════
    # 6. GUJARAT TITANS (GT)
    # ══════════════════════════════════════════════════════════
    'Shubman Gill':     ('GT',  'batter',       'none',  'none'),
    'B Sai Sudharsan':  ('GT',  'batter',       'none',  'none'),
    'M Shahrukh Khan':  ('GT',  'batter',       'none',  'none'),
    'JC Buttler':       ('GT',  'wicketkeeper', 'none',  'none'),
    'Kumar Kushagra':   ('GT',  'wicketkeeper', 'none',  'none'),
    'Anuj Rawat':       ('GT',  'wicketkeeper', 'none',  'none'),
    'T Banton':         ('GT',  'wicketkeeper', 'none',  'none'),
    'R Tewatia':        ('GT',  'allrounder',   'spin',  'leg-spin'),
    'Washington Sundar':('GT',  'allrounder',   'spin',  'off-spin'),
    'N Sindhu':         ('GT',  'allrounder',   'spin',  'off-spin'),
    'GD Phillips':      ('GT',  'allrounder',   'spin',  'off-spin'),
    'J Yadav':          ('GT',  'allrounder',   'spin',  'off-spin'),
    'JO Holder':        ('GT',  'allrounder',   'pace',  'fast-medium'),
    'R Sai Kishore':    ('GT',  'bowler',        'spin',  'slow-left-arm-orthodox'),
    'Rashid Khan':      ('GT',  'bowler',        'spin',  'leg-spin'),
    'Mohammed Siraj':   ('GT',  'bowler',        'pace',  'fast-medium'),
    'K Rabada':         ('GT',  'bowler',        'pace',  'fast'),
    'Mohammed Shami':   ('GT',  'bowler',        'pace',  'fast-medium'),
    'M Prasidh Krishna':('GT',  'bowler',        'pace',  'fast-medium'),
    'Gurnoor Brar':     ('GT',  'bowler',        'pace',  'fast-medium'),
    'I Sharma':         ('GT',  'bowler',        'pace',  'fast-medium'),
    'Ashok Sharma':     ('GT',  'bowler',        'pace',  'fast-medium'),
    'L Wood':           ('GT',  'bowler',        'pace',  'fast'),
    'K Khejroliya':     ('GT',  'bowler',        'pace',  'fast-medium'),
    'Arshad Khan':      ('GT',  'bowler',        'spin',  'off-spin'),

    # ══════════════════════════════════════════════════════════
    # 7. RAJASTHAN ROYALS (RR)
    # ══════════════════════════════════════════════════════════
    'YBK Jaiswal':      ('RR',  'batter',       'none',  'none'),
    'SO Hetmyer':       ('RR',  'batter',       'none',  'none'),
    'V Suryavanshi':    ('RR',  'batter',       'none',  'none'),
    'Dhruv Jurel':      ('RR',  'wicketkeeper', 'none',  'none'),
    'D Ferreira':       ('RR',  'wicketkeeper', 'none',  'none'),
    'R Parag':          ('RR',  'allrounder',   'spin',  'off-spin'),
    'RA Jadeja':        ('RR',  'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'SM Curran':        ('RR',  'allrounder',   'pace',  'fast-medium'),
    'Sandeep Sharma':   ('RR',  'bowler',        'pace',  'fast-medium'),
    'N Burger':         ('RR',  'bowler',        'pace',  'fast-medium'),
    'JC Archer':        ('RR',  'bowler',        'pace',  'fast'),
    'TU Deshpande':     ('RR',  'bowler',        'pace',  'fast-medium'),
    'KT Maphaka':       ('RR',  'bowler',        'pace',  'fast'),
    'Ravi Bishnoi':     ('RR',  'bowler',        'spin',  'leg-spin'),
    'Yash Raj Punja':   ('RR',  'bowler',        'pace',  'fast-medium'),
    'V Puthur':         ('RR',  'bowler',        'pace',  'fast-medium'),
    'Brijesh Sharma':   ('RR',  'bowler',        'pace',  'fast-medium'),
    'AF Milne':         ('RR',  'bowler',        'pace',  'fast-medium'),

    # ══════════════════════════════════════════════════════════
    # 8. DELHI CAPITALS (DC)
    # ══════════════════════════════════════════════════════════
    'PP Shaw':          ('DC',  'batter',       'none',  'none'),
    'DA Miller':        ('DC',  'batter',       'none',  'none'),
    'P Nissanka':       ('DC',  'batter',       'none',  'none'),
    'KK Nair':          ('DC',  'batter',       'none',  'none'),
    'SU Parakh':        ('DC',  'batter',       'none',  'none'),
    'N Rana':           ('DC',  'allrounder',   'spin',  'off-spin'),
    'Sameer Rizvi':     ('DC',  'batter',       'none',  'none'),
    'Ashutosh Sharma':  ('DC',  'allrounder',   'pace',  'fast-medium'),
    'KL Rahul':         ('DC',  'wicketkeeper', 'none',  'none'),
    'T Stubbs':         ('DC',  'wicketkeeper', 'none',  'none'),
    'Abishek Porel':    ('DC',  'wicketkeeper', 'none',  'none'),
    'AR Patel':         ('DC',  'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'V Nigam':          ('DC',  'allrounder',   'spin',  'leg-spin'),
    'T Vijay':          ('DC',  'allrounder',   'spin',  'off-spin'),
    'Auqib Nabi':       ('DC',  'allrounder',   'pace',  'fast-medium'),
    'Kuldeep Yadav':    ('DC',  'bowler',        'spin',  'left-arm-wrist-spin'),
    'MA Starc':         ('DC',  'bowler',        'pace',  'fast'),
    'Mukesh Kumar':     ('DC',  'bowler',        'pace',  'fast-medium'),
    'L Ngidi':          ('DC',  'bowler',        'pace',  'fast-medium'),
    'KA Jamieson':      ('DC',  'bowler',        'pace',  'fast-medium'),
    'PVD Chameera':     ('DC',  'bowler',        'pace',  'fast'),

    # ══════════════════════════════════════════════════════════
    # 9. PUNJAB KINGS (PBKS)
    # ══════════════════════════════════════════════════════════
    'SS Iyer':          ('PBKS','batter',       'none',  'none'),
    'N Wadhera':        ('PBKS','batter',       'none',  'none'),
    'Shashank Singh':   ('PBKS','batter',       'none',  'none'),
    'P Simran Singh':   ('PBKS','wicketkeeper', 'none',  'none'),
    'Vishnu Vinod':     ('PBKS','wicketkeeper', 'none',  'none'),
    'MP Stoinis':       ('PBKS','allrounder',   'pace',  'fast-medium'),
    'Harpreet Brar':    ('PBKS','allrounder',   'spin',  'slow-left-arm-orthodox'),
    'M Jansen':         ('PBKS','allrounder',   'pace',  'fast-medium'),
    'Azmatullah Omarzai':('PBKS','allrounder',  'pace',  'fast-medium'),
    'Priyansh Arya':    ('PBKS','allrounder',   'pace',  'fast-medium'),
    'Musheer Khan':     ('PBKS','allrounder',   'spin',  'slow-left-arm-orthodox'),
    'Suryansh Shedge':  ('PBKS','allrounder',   'pace',  'fast-medium'),
    'BJ Dwarshuis':     ('PBKS','allrounder',   'pace',  'fast-medium'),
    'Arshdeep Singh':   ('PBKS','bowler',        'pace',  'fast-medium'),
    'YS Chahal':        ('PBKS','bowler',        'spin',  'leg-spin'),
    'Vijaykumar Vyshak':('PBKS','bowler',        'pace',  'fast-medium'),
    'Yash Thakur':      ('PBKS','bowler',        'pace',  'fast-medium'),
    'XC Bartlett':      ('PBKS','bowler',        'pace',  'fast-medium'),
    'P Dubey':          ('PBKS','bowler',        'spin',  'off-spin'),
    'LH Ferguson':      ('PBKS','bowler',        'pace',  'fast'),

    # ══════════════════════════════════════════════════════════
    # 10. LUCKNOW SUPER GIANTS (LSG)
    # ══════════════════════════════════════════════════════════
    'AK Markram':       ('LSG', 'allrounder',   'spin',  'off-spin'),
    'Himmat Singh':     ('LSG', 'batter',       'none',  'none'),
    'MP Breetzke':      ('LSG', 'batter',       'none',  'none'),
    'Akshat Raghuwanshi':('LSG','batter',       'none',  'none'),
    'RR Pant':          ('LSG', 'wicketkeeper', 'none',  'none'),
    'N Pooran':         ('LSG', 'wicketkeeper', 'none',  'none'),
    'JP Inglis':        ('LSG', 'wicketkeeper', 'none',  'none'),
    'MR Marsh':         ('LSG', 'allrounder',   'pace',  'fast-medium'),
    'Abdul Samad':      ('LSG', 'allrounder',   'pace',  'fast-medium'),
    'Shahbaz Ahmed':    ('LSG', 'allrounder',   'spin',  'slow-left-arm-orthodox'),
    'PWH de Silva':     ('LSG', 'allrounder',   'spin',  'off-spin'),
    'A Badoni':         ('LSG', 'allrounder',   'pace',  'fast-medium'),
    'Mohammed Shami':   ('LSG', 'bowler',        'pace',  'fast-medium'),
    'Avesh Khan':       ('LSG', 'bowler',        'pace',  'fast-medium'),
    'MP Yadav':         ('LSG', 'bowler',        'pace',  'fast'),
    'Mohsin Khan':      ('LSG', 'bowler',        'pace',  'fast-medium'),
    'M Siddharth':      ('LSG', 'bowler',        'spin',  'slow-left-arm-orthodox'),
    'Akash Singh':      ('LSG', 'bowler',        'pace',  'fast-medium'),
    'Prince Yadav':     ('LSG', 'bowler',        'pace',  'fast-medium'),
    'A Nortje':         ('LSG', 'bowler',        'pace',  'fast'),
}


# ── Additional name aliases not in Cricsheet ─────────────────
# These players appear in the squad list but may have different
# Cricsheet names or are new — map them to closest Cricsheet name
ALIASES = {
    # CSK
    'Sarfaraz Khan':    'SK Rasheed',      # Not in Cricsheet — new player
    'Dian Forrester':   None,              # Not in Cricsheet dataset
    'Macneil Noronha':  None,
    'Zak Foulkes':      None,
    'Spencer Johnson':  None,
    'Kuldip Yadav':     None,
    'Matt Henry':       'MJ Henry',
    'Akeal Hosein':     'AJ Hosein',
    'Rahul Chahar':     'RD Chahar',
    'Khaleel Ahmed':    'KK Ahmed',
    'Anshul Kamboj':    'A Kamboj',
    'Mukesh Choudhary': 'MD Choudhary',
    'Shreyas Gopal':    'S Gopal',
    'Ruturaj Gaikwad':  'RD Gaikwad',
    'Dewald Brevis':    'D Brevis',
    'Ayush Mhatre':     'A Mhatre',
    'Mahendra Singh Dhoni': 'MS Dhoni',
    'Sanju Samson':     'SV Samson',
    'Shivam Dube':      'S Dube',
    'Matthew Short':    'MW Short',
    'Prashant Veer':    'PR Veer',
    # MI
    'Rohit Sharma':     'RG Sharma',
    'Suryakumar Yadav': 'SA Yadav',
    'Sherfane Rutherford': 'SE Rutherford',
    'Quinton de Kock':  'Q de Kock',
    'Ryan Rickelton':   'RD Rickelton',
    'Robin Minz':       'R Minz',
    'Hardik Pandya':    'HH Pandya',
    'Will Jacks':       'WG Jacks',
    'Mitchell Santner': 'MJ Santner',
    'Shardul Thakur':   'SN Thakur',
    'Raj Angad Bawa':   'RA Bawa',
    'Corbin Bosch':     'C Bosch',
    'Jasprit Bumrah':   'JJ Bumrah',
    'Trent Boult':      'TA Boult',
    'Deepak Chahar':    'DL Chahar',
    'Mayank Markande':  'M Markande',
    'Allah Ghazanfar':  'AM Ghazanfar',
    'Raghu Sharma':     'Raghu Sharma',
    # RCB
    'Rajat Patidar':    'RM Patidar',
    'Virat Kohli':      'V Kohli',
    'Devdutt Padikkal': 'D Padikkal',
    'Phil Salt':        'PD Salt',
    'Jitesh Sharma':    'JM Sharma',
    'Krunal Pandya':    'KH Pandya',
    'Venkatesh Iyer':   'VR Iyer',
    'Tim David':        'TH David',
    'Romario Shepherd': 'R Shepherd',
    'Jacob Bethell':    'JG Bethell',
    'Josh Hazlewood':   'JR Hazlewood',
    'Bhuvneshwar Kumar':'B Kumar',
    'Yash Dayal':       'Yash Dayal',
    'Rasikh Dar':       'Rasikh Salam',
    'Nuwan Thushara':   'N Thushara',
    'Jacob Duffy':      'JA Duffy',
    'Richard Gleeson':  'RJ Gleeson',
    # KKR
    'Ajinkya Rahane':   'AM Rahane',
    'Rinku Singh':      'RK Singh',
    'Angkrish Raghuvanshi': 'A Raghuvanshi',
    'Manish Pandey':    'MK Pandey',
    'Rahul Tripathi':   'RA Tripathi',
    'Rovman Powell':    'R Powell',
    'Tim Seifert':      'TL Seifert',
    'Sunil Narine':     'SP Narine',
    'Cameron Green':    'C Green',
    'Rachin Ravindra':  'R Ravindra',
    'Varun Chakaravarthy': 'CV Varun',
    'Matheesha Pathirana': 'M Pathirana',
    'Vaibhav Arora':    'VG Arora',
    'Navdeep Saini':    'Navdeep Saini',
    'Blessing Muzarabani': 'B Muzarabani',
    'Harshit Rana':     'Harshit Rana',
    # SRH
    'Travis Head':      'TM Head',
    'Heinrich Klaasen': 'H Klaasen',
    'Nitish Kumar Reddy':'Nithish Kumar Reddy',
    'Pat Cummins':      'PJ Cummins',
    'T. Natarajan':     'T Natarajan',
    'Jaydev Unadkat':   'JD Unadkat',
    'Zeeshan Ansari':   'Zeeshan Ansari',
    'Eshan Malinga':    'E Malinga',
    'Praful Hinge':     'PP Hinge',
    # GT
    'Shubman Gill':     'Shubman Gill',
    'Sai Sudharsan':    'B Sai Sudharsan',
    'Shahrukh Khan':    'M Shahrukh Khan',
    'Jos Buttler':      'JC Buttler',
    'Rahul Tewatia':    'R Tewatia',
    'Washington Sundar':'Washington Sundar',
    'Nishant Sindhu':   'N Sindhu',
    'Glenn Phillips':   'GD Phillips',
    'Jayant Yadav':     'J Yadav',
    'Jason Holder':     'JO Holder',
    'R. Sai Kishore':   'R Sai Kishore',
    'Mohammed Siraj':   'Mohammed Siraj',
    'Kagiso Rabada':    'K Rabada',
    'Mohammed Shami':   'Mohammed Shami',
    'Prasidh Krishna':  'M Prasidh Krishna',
    'Gurnoor Singh Brar':'Gurnoor Brar',
    'Ishant Sharma':    'I Sharma',
    'Luke Wood':        'L Wood',
    'Kulwant Khejroliya':'K Khejroliya',
    'Mohd. Arshad Khan':'Arshad Khan',
    # RR
    'Yashasvi Jaiswal': 'YBK Jaiswal',
    'Shimron Hetmyer':  'SO Hetmyer',
    'Vaibhav Suryavanshi':'V Suryavanshi',
    'Dhruv Jurel':      'Dhruv Jurel',
    'Donovan Ferreira': 'D Ferreira',
    'Riyan Parag':      'R Parag',
    'Ravindra Jadeja':  'RA Jadeja',
    'Sam Curran':       'SM Curran',
    'Sandeep Sharma':   'Sandeep Sharma',
    'Nandre Burger':    'N Burger',
    'Jofra Archer':     'JC Archer',
    'Tushar Deshpande': 'TU Deshpande',
    'Kwena Maphaka':    'KT Maphaka',
    'Ravi Bishnoi':     'Ravi Bishnoi',
    'Vignesh Puthur':   'V Puthur',
    'Brijesh Sharma':   'Brijesh Sharma',
    'Adam Milne':       'AF Milne',
    # DC
    'Prithvi Shaw':     'PP Shaw',
    'David Miller':     'DA Miller',
    'Pathum Nissanka':  'P Nissanka',
    'Karun Nair':       'KK Nair',
    'Sahil Parakh':     'SU Parakh',
    'Nitish Rana':      'N Rana',
    'KL Rahul':         'KL Rahul',
    'Tristan Stubbs':   'T Stubbs',
    'Axar Patel':       'AR Patel',
    'Vipraj Nigam':     'V Nigam',
    'Tripurana Vijay':  'T Vijay',
    'Auqib Dar':        'Auqib Nabi',
    'Kuldeep Yadav':    'Kuldeep Yadav',
    'Mitchell Starc':   'MA Starc',
    'Lungi Ngidi':      'L Ngidi',
    'Kyle Jamieson':    'KA Jamieson',
    'Dushmantha Chameera':'PVD Chameera',
    # PBKS
    'Shreyas Iyer':     'SS Iyer',
    'Nehal Wadhera':    'N Wadhera',
    'Shashank Singh':   'Shashank Singh',
    'Prabhsimran Singh':'P Simran Singh',
    'Marcus Stoinis':   'MP Stoinis',
    'Marco Jansen':     'M Jansen',
    'Azmatullah Omarzai':'Azmatullah Omarzai',
    'Arshdeep Singh':   'Arshdeep Singh',
    'Yuzvendra Chahal': 'YS Chahal',
    'Vyshak Vijaykumar':'Vijaykumar Vyshak',
    'Xavier Bartlett':  'XC Bartlett',
    'Pravin Dubey':     'P Dubey',
    'Lockie Ferguson':  'LH Ferguson',
    # LSG
    'Aiden Markram':    'AK Markram',
    'Matthew Breetzke': 'MP Breetzke',
    'Rishabh Pant':     'RR Pant',
    'Nicholas Pooran':  'N Pooran',
    'Josh Inglis':      'JP Inglis',
    'Mitchell Marsh':   'MR Marsh',
    'Shahbaz Ahamad':   'Shahbaz Ahmed',
    'Wanindu Hasaranga':'PWH de Silva',
    'Ayush Badoni':     'A Badoni',
    'Mohammad Shami':   'Mohammed Shami',
    'Avesh Khan':       'Avesh Khan',
    'Mayank Yadav':     'MP Yadav',
    'Mohsin Khan':      'Mohsin Khan',
    'M. Siddharth':     'M Siddharth',
    'Akash Singh':      'Akash Singh',
    'Prince Yadav':     'Prince Yadav',
    'Anrich Nortje':    'A Nortje',
}


print("=" * 60)
print("CricketIQ X - Current IPL Squad Classifier")
print("=" * 60)

db = SessionLocal()
players = db.query(Player).all()
name_to_player = {p.name: p for p in players}

updated      = 0
not_found    = []
team_counts  = {}

for cricsheet_name, (team, role, bowl_type, bowl_sub) in CURRENT_SQUADS.items():
    p = name_to_player.get(cricsheet_name)
    if not p:
        not_found.append(cricsheet_name)
        continue

    p.ipl_team      = team
    p.role          = role
    p.bowling_style = f"{bowl_type}:{bowl_sub}" if bowl_type != 'none' else 'none'

    team_counts[team] = team_counts.get(team, 0) + 1
    updated += 1

db.commit()
db.close()

print(f"\nUpdated {updated} players.")
print(f"\nPlayers per team:")
for team, count in sorted(team_counts.items()):
    print(f"  {team:6s}: {count} players")

if not_found:
    print(f"\nNot found in DB ({len(not_found)}):")
    for name in not_found:
        print(f"  - {name}")

print("\nVerifying team assignments...")
db2 = SessionLocal()
for team in ['CSK','MI','RCB','KKR','SRH','GT','RR','DC','PBKS','LSG']:
    count = db2.query(Player).filter(Player.ipl_team == team).count()
    print(f"  {team:6s}: {count} players in DB")
db2.close()

print("\nDone!")