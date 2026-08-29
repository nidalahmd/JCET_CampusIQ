import logging
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.entities import Document, DocumentChunk, ProcessingStatus, User, UserRole
from app.services.ingestion import ingest_document_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("campusiq.import_demo")

DEMO_DOCUMENTS = [
    {
        "title": "JCET Institutional Academic Handbook 2025-26",
        "file_name": "JCET_Academic_Handbook_2025_26.md",
        "category": "Academics",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# Jawaharlal College of Engineering and Technology (JCET) — Institutional Academic Handbook

## 1. Institutional Profile and Legacy
Jawaharlal College of Engineering and Technology (JCET), Jawahar Gardens, Lakkidi, Mangalam, Palakkad, Kerala (PIN: 679301), is a premier engineering institution established by the Nehru Group of Institutions (NGI). Approved by the All India Council for Technical Education (AICTE), New Delhi, and affiliated to APJ Abdul Kalam Technological University (KTU), Kerala, JCET holds NAAC A+ Accreditation and Autonomous status.

## 2. Vision of the Institution
To emerge as a centre of excellence for professional education to produce high-quality engineers and entrepreneurs for the sustainable development of the region and the Nation.

## 3. Mission of the Institution
- To become an ultimate destination for acquiring the latest and advanced knowledge in multidisciplinary engineering domains.
- To impart value-based technical education and cultivate research, creativity, and leadership skills.
- To foster ethical values, entrepreneurial mindsets, and social commitment among students.

## 4. Quality Policy
JCET is committed to delivering quality technical education matching global standards through continuous improvement of faculty competence, state-of-the-art laboratory infrastructure, industry collaboration, and student-centric pedagogical practices.

## 5. Campus Facilities and Infrastructure
The college spans a 60-acre lush green eco-friendly campus with modern smart classrooms, high-speed Wi-Fi, centralized computing facilities, language laboratories, modern hostels for boys and girls, sports grounds, and multi-cuisine cafeterias. JCET houses an Aeronautical Engineering hangar featuring a real Learjet aircraft, wind tunnel, and aircraft structural testing facilities.

## 6. Central Library Policies and Working Hours
- **Working Hours:** 8:30 AM to 6:00 PM on all working days. Digital library services remain accessible 24/7.
- **Book Borrowing Privileges:** Undergraduate students can borrow up to 3 books for 14 days. Renewal is permitted once if no prior reservation exists.
- **Reference Section:** Dictionaries, encyclopedias, yearbooks, and university question paper archives are strictly for in-library reference.
- **Digital Library:** Subscriptions include IEEE Xplore, ScienceDirect, DELNET, and NPTEL local video servers with 40 dedicated high-performance workstations.

## 7. Hostel Rules and Code of Conduct
- In-campus hostels provide furnished accommodation with biometric access control, 24/7 security, and mess facilities.
- **Curfew Timings:** All resident students must return to the hostel premises by 6:30 PM. Late entry requires prior approval from the Chief Warden.
- Absolute silence must be maintained in study halls between 8:30 PM and 11:00 PM.
- Possession or consumption of alcohol, tobacco, narcotics, or unauthorized electrical appliances is strictly prohibited and attracts immediate expulsion.

## 8. Anti-Ragging Policy and Statutory Compliance
Ragging in any form inside or outside the college campus and hostels is strictly prohibited by law (Kerala Prohibition of Ragging Act, 1998 and AICTE regulations). Any student found guilty of ragging is liable for immediate suspension, registration of a police complaint, and permanent expulsion from the institution. The Anti-Ragging Squad conducts 24/7 surprise surveillance across campus.
""",
    },
    {
        "title": "JCET B.Tech Academic Regulations 2025",
        "file_name": "JCET_BTech_Regulations_2025.md",
        "category": "Regulations",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# JCET Autonomous & KTU B.Tech Academic Regulations 2025

## 1. Structure of the B.Tech Program
The B.Tech program follows a semester-based credit system over 4 academic years (8 semesters). The total credits required for the award of standard B.Tech degree is 160 credits. For B.Tech (Honours) or B.Tech with Minor, a student must earn an additional 20 credits (Total: 180 credits).

## 2. Course Credit Distribution
- **Theory Courses (3-4 lecture hours/week):** 3 to 4 credits.
- **Practical / Laboratory Courses (2-3 lab hours/week):** 1 to 2 credits.
- **Mini Project & Design Project:** 2 credits.
- **Final Year Major Project:** 6 credits across Semester 7 and 8.
- **Mandatory Non-Credit Courses:** Constitution of India, Environmental Studies, Professional Ethics, Life Skills, and Student Activity Points (min 100 points).

## 3. Attendance Requirements and Condonation
- A student must secure a minimum of **75% attendance** in each registered course to be eligible to appear for the End Semester Examination (ESE).
- **Condonation of Attendance:** Shortage of attendance between 65% and 74% may be condoned by the Principal up to a maximum of two times during the entire 4-year program, strictly on valid medical grounds supported by a medical certificate from a registered medical practitioner.
- Students securing less than 65% attendance are not eligible for condonation and must repeat the course when offered in subsequent semesters (Course Repeat / FE grade).

## 4. Assessment and Evaluation Framework
Evaluation consists of two major components:
- **Continuous Internal Evaluation (CIE):** 40% (or 50% for select autonomous practical streams).
- **End Semester Examination (ESE):** 60% (or 50%).
- **CIE Components:** Series Test 1 (20 marks), Series Test 2 (20 marks), Continuous assignments/quizzes/micro-projects (10 marks). Total CIE: 50 scaled to 40/50.

## 5. Grading System and Passing Criteria
Performance in each course is awarded a letter grade based on total marks obtained (CIE + ESE):
- **O (Outstanding):** 90% and above | Grade Point: 10
- **A+ (Excellent):** 85% to 89% | Grade Point: 9.0
- **A (Very Good):** 80% to 84% | Grade Point: 8.5
- **B+ (Good):** 70% to 79% | Grade Point: 8.0
- **B (Above Average):** 60% to 69% | Grade Point: 7.0
- **C (Average):** 50% to 59% | Grade Point: 6.0
- **P (Pass):** 45% to 49% | Grade Point: 5.0
- **F (Fail):** Below 45% total, or below 40% in ESE | Grade Point: 0

**Passing Minimum:** A student must secure a minimum of 40% marks in the End Semester Examination and 45% marks in aggregate (CIE + ESE) to pass the course.

## 6. Promotion to Higher Semesters (Credit Thresholds)
- **Promotion to Semester 3:** Minimum 20 credits earned from Semester 1 and 2.
- **Promotion to Semester 5:** Minimum 45 credits earned from Semester 1 to 4.
- **Promotion to Semester 7:** Minimum 75 credits earned from Semester 1 to 6.

## 7. B.Tech Honours and Minor Programs
- Students with CGPA >= 8.5 at the end of Semester 4 without any active backlogs are eligible to register for B.Tech Honours in their parent branch or Minor in an allied engineering discipline.
- Registration allows taking one additional theory course per semester from Semester 5 to 8 plus a specialized project in Semester 8.
""",
    },
    {
        "title": "JCET Institutional Academic Calendar 2025-26",
        "file_name": "JCET_Academic_Calendar_2025_26.md",
        "category": "Academics",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# Jawaharlal College of Engineering and Technology — Academic Calendar 2025-26

## 1. Odd Semester Schedule (Semesters 1, 3, 5, 7)
- **Commencement of Classes:** August 1, 2025
- **First Internal Series Test (Test 1):** September 22 – September 26, 2025
- **Publication of Test 1 Results & Parent-Teacher Meeting (PTM 1):** October 6, 2025
- **Mid-Semester Feedback Collection:** October 10, 2025
- **Second Internal Series Test (Test 2):** November 17 – November 21, 2025
- **Publication of Test 2 Results & Internal CIE Marks:** November 28, 2025
- **Last Date for Attendance Condonation Application:** November 30, 2025
- **Last Instructional Day (Class Dispersal):** December 5, 2025
- **Practical / Laboratory End Semester Examinations:** December 8 – December 15, 2025
- **University / Autonomous Theory End Semester Examinations:** December 18, 2025 – January 9, 2026
- **Winter Semester Vacation:** January 10 – January 25, 2026

## 2. Even Semester Schedule (Semesters 2, 4, 6, 8)
- **Commencement of Classes:** January 28, 2026
- **First Internal Series Test (Test 1):** March 16 – March 20, 2026
- **JCET Annual Tech Fest & Cultural Conclave (IGNITE):** March 27 – March 28, 2026
- **Publication of Test 1 Results & PTM 2:** April 3, 2026
- **Second Internal Series Test (Test 2):** May 11 – May 15, 2026
- **Final CIE & Attendance Publishing:** May 22, 2026
- **Last Instructional Day:** May 29, 2026
- **Practical End Semester Examinations:** June 1 – June 8, 2026
- **Theory End Semester Examinations:** June 11 – June 30, 2026
- **Summer Internship / Project Break:** July 1 – July 31, 2026

## 3. Working Hours and Instructional Norms
- Regular class hours: 9:00 AM to 4:30 PM (Monday through Friday).
- Minimum instructional days per semester: 75 working days (excluding examination days).
""",
    },
    {
        "title": "JCET Institutional Overview and Brochure",
        "file_name": "JCET_Brochure_Overview.md",
        "category": "Brochure",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# Jawaharlal College of Engineering and Technology — Institutional Brochure

## 1. About Nehru Group of Institutions (NGI)
Founded in 1968 by Late Shri P. K. Das, a visionary academician, the Nehru Group of Institutions (NGI) has grown into a prestigious educational conglomerate comprising over 20 institutions across Kerala and Tamil Nadu. JCET in Palakkad stands as a flagship autonomous engineering campus under NGI.

## 2. Key Accreditations and Approvals
- **AICTE Approval:** Permanent approval from AICTE, Ministry of Education, Govt. of India.
- **Accreditation:** NAAC 'A+' Grade accredited institution with high benchmark scores in teaching-learning, research, and governance.
- **Autonomous Status:** Conferred autonomous status for progressive curriculum design aligned with industry 4.0 standards.
- **ISO Certification:** ISO 9001:2015 certified for educational administration quality.

## 3. Academic Programs Offered
### Undergraduate (B.Tech) Programs:
- Computer Science and Engineering (CSE)
- CSE (Artificial Intelligence & Machine Learning)
- CSE (Cyber Security)
- Aeronautical Engineering (flagship with aircraft hangar & Learjet)
- Electronics and Communication Engineering (ECE)
- Mechanical Engineering
- Civil Engineering
- Electrical and Electronics Engineering (EEE)

### Postgraduate Programs:
- M.Tech in Computer Science & Engineering
- M.Tech in Applied Electronics & Communication
- MBA (Master of Business Administration - Dual Specialization in Finance, HR, Marketing, Systems, Logistics)
- MCA (Master of Computer Applications)

## 4. Placement and Career Development (NCPIR)
The Nehru Corporate Placements and Industrial Relations (NCPIR) cell maintains tie-ups with leading global corporations. Over 150+ marquee recruiters visit annually, including TCS, Infosys, Wipro, Cognizant, Capgemini, Quest Global, Hexaware, Zoho, UST Global, and IBS Software. Highest compensation packages reach 12 LPA with an average placement rate exceeding 85% for eligible students.
""",
    },
    {
        "title": "JCET Official Examination Manual and Assessment Rules",
        "file_name": "JCET_Examination_Manual.md",
        "category": "Examinations",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# JCET Examination Manual and Assessment Procedures

## 1. Continuous Internal Evaluation (CIE) Calculation
Internal marks (40 or 50 maximum marks) are computed scientifically:
- **Two Centralized Series Tests:** Conducted by the Examination Cell under strict hall invigilation. Each test carries 50 marks and is scaled to 20 marks (Total 40 marks from both tests).
- **Assignments / Tutorials / Micro-projects:** Minimum of two documented assignments evaluated on rubric-based criteria (Total 10 marks).
- All internal marks and attendance statistics are published on the CampusIQ portal prior to university submission for student verification.

## 2. End Semester Examination (ESE) Conduct
- Hall tickets are generated only for students who fulfill the 75% attendance criterion and have cleared all institutional dues.
- Students must occupy their designated exam desks 15 minutes before the exam commences.
- Entry into the examination hall is barred 30 minutes after the commencement of the exam.
- Students are strictly forbidden from carrying mobile phones, programmable calculators, smartwatches, or handwritten chits into the exam halls.

## 3. Examination Malpractice and Penalties
Any student found engaging in unfair practices (copying, possessing prohibited electronic devices, impersonation) is immediately handed over to the College Examination Malpractice Committee (CEMC). Penalties include cancellation of the examination for that paper, debarment from remaining examinations of the semester, and possible suspension for up to one academic year.

## 4. Revaluation and Answer Script Scrutiny
- Students can apply for copy of evaluated answer scripts and revaluation within 7 days of result declaration.
- If the difference in revaluation marks exceeds 15% of the maximum marks, the paper is sent for a third valuation, and the average of the closest two scores is awarded.

## 5. SGPA and CGPA Calculation Formulas
- **Semester Grade Point Average (SGPA):** $\text{SGPA} = \frac{\sum (C_i \times GP_i)}{\sum C_i}$ for all courses registered in that semester.
- **Cumulative Grade Point Average (CGPA):** $\text{CGPA} = \frac{\sum (C_i \times GP_i)}{\sum C_i}$ computed across all completed semesters.
- **Conversion from CGPA to Percentage Marks:** $\text{Percentage (\%)} = (\text{CGPA} - 0.5) \times 10$.
""",
    },
    {
        "title": "JCET Official Admission Guidelines and Quota Details",
        "file_name": "JCET_Admission_Guidelines.md",
        "category": "Admissions",
        "department": "All Departments",
        "academic_year": "2025-2026",
        "content": """# JCET Admissions Guidelines, Eligibility & Quota Distribution

## 1. Admission Eligibility Criteria
### B.Tech Programs:
- Candidates must have passed Higher Secondary Examination (10+2) of Kerala or examinations recognized as equivalent thereto with Mathematics, Physics, and Chemistry (or Computer Science/Biotechnology) as optional subjects.
- Minimum aggregate marks in MPC: **50% marks** (45% marks for SEBC and reservation categories).
- Valid score in Kerala Engineering Architecture Medical (**KEAM**) entrance examination conducted by the Commissioner for Entrance Examinations (CEE), Kerala.

### B.Tech Lateral Entry (Direct 2nd Year):
- Diploma in Engineering / Technology with minimum 45% marks awarded by the State Board of Technical Education, or B.Sc. with Mathematics.
- Qualified in Kerala Lateral Entry Test (LET).

## 2. Seat Allocation and Quotas
- **Government Merit Quota (50% of total seats):** Allotted through Centralized Allotment Process (CAP) conducted by CEE Kerala based on KEAM rank.
- **Management Quota (35% of total seats):** Allotted directly by the institution based on academic merit in plus-two and KEAM/JEE scores.
- **NRI Quota (15% of total seats):** Reserved for children/dependents of Non-Resident Indians without mandatory KEAM qualification, subject to AICTE/Govt norms.

## 3. Mandatory Documents Checklist at Time of Admission
1. SSLC / 10th Standard Certificate and Mark List (Original + 3 copies)
2. Higher Secondary / 12th Standard Mark Sheet and Pass Certificate (Original + 3 copies)
3. KEAM Admit Card, Score Card, and CEE Allotment Memo
4. Transfer Certificate (TC) and Conduct Certificate from the last attended institution
5. Migration Certificate (for boards other than Kerala State HSE)
6. Physical Fitness Certificate from an authorized Medical Officer
7. Category / Caste / Income Certificate (for reservation and scholarship claimants)
8. Passport size photographs (6 copies)

## 4. Scholarships and Fee Waivers
- **Nehru Vigyan Scholarship:** Merit scholarship for students with KEAM ranks below 10,000 (100% tuition fee waiver).
- **Girl Student Empowerment Scheme:** Special financial assistance for meritorious female engineering aspirants.
- **Economically Weaker Section (EWS) Scheme:** Subsidized education for economically challenged backgrounds.
""",
    },
    {
        "title": "JCET Department of Computer Science and Engineering Manual",
        "file_name": "JCET_CSE_Department_Manual.md",
        "category": "Academics",
        "department": "Computer Science & Engineering",
        "academic_year": "2025-2026",
        "content": """# Department of Computer Science and Engineering — Manual

## 1. Department Overview
The Department of Computer Science and Engineering (CSE) at JCET was established in 2008. The department offers undergraduate B.Tech in CSE, specialized B.Tech programs in Cyber Security and Data Science, and postgraduate M.Tech in Computer Science. The department is equipped with high-end computational infrastructure, advanced AI research workstations, and active technical society student chapters.

## 2. Department Vision
To produce competent computer science professionals with research and innovative skills, by providing them with the most conducive environment for quality academic and research-oriented undergraduate and postgraduate education along with moral values committed to build a vibrant nation.

## 3. Department Mission
- To provide a state-of-the-art learning environment to develop creativity, algorithmic thinking, and problem-solving skills in a professional manner.
- To promote industry-academia collaboration, applied research, and entrepreneurship in cutting-edge computing domains.
- To instill ethical values, lifelong learning habits, and social responsibility in computer science graduates.

## 4. Program Educational Objectives (PEOs)
- **PEO 1:** Graduates will establish successful careers in software engineering, artificial intelligence, cyber security, data analytics, or pursue higher education and research.
- **PEO 2:** Graduates will design robust, scalable, and secure computational solutions to real-world engineering and business problems.
- **PEO 3:** Graduates will demonstrate professional ethics, effective communication, and multidisciplinary teamwork skills.

## 5. Specialized Laboratories and Computing Facilities
1. **Artificial Intelligence & Deep Learning Lab:** Equipped with NVIDIA GPU workstations, CUDA toolkits, and Python AI frameworks.
2. **Cloud & High Performance Computing Lab:** OpenStack private cloud environment for distributed systems and virtualization research.
3. **Cyber Security & Ethical Hacking Lab:** Isolated network infrastructure for penetration testing, digital forensics, and cryptographic protocol analysis.
4. **Data Analytics & Database Engineering Lab:** PostgreSQL, MongoDB, Hadoop, Spark clusters for big data analytics.
5. **Software Engineering & Web Technologies Lab:** Full-stack development environment supporting Linux, React, Node.js, and DevOps CI/CD pipelines.

## 6. Student Chapters and Technical Forums
- **ACM Student Chapter:** Organizes competitive programming contests, hackathons, and research webinars.
- **Computer Society of India (CSI) Student Branch:** Conducts technical paper presentations and coding workshops.
- **FOSS Cell (Free and Open Source Software):** Promotes Linux adoption, open-source contributions, and kernel development.
""",
    },
]


def run():
    with SessionLocal() as db:
        # Ensure Admin User exists
        admin_user = db.scalar(select(User).where(User.role == UserRole.ADMIN))
        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                name="JCET Administrator",
                email="admin@jcet.ac.in",
                password_hash=hash_password("Admin@JCET2026"),
                role=UserRole.ADMIN,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            logger.info("Created default admin user: admin@jcet.ac.in")

        upload_dir = Path("./uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        ingested_count = 0
        total_chunks = 0

        for item in DEMO_DOCUMENTS:
            file_path = upload_dir / item["file_name"]
            file_path.write_text(item["content"].strip(), encoding="utf-8")

            # Check if document already exists
            existing_doc = db.scalar(select(Document).where(Document.file_name == item["file_name"]))
            if existing_doc:
                existing_doc.title = item["title"]
                existing_doc.category = item["category"]
                existing_doc.department = item["department"]
                existing_doc.academic_year = item["academic_year"]
                existing_doc.storage_path = str(file_path)
                existing_doc.processing_status = ProcessingStatus.UPLOADED
                db.add(existing_doc)
                db.commit()
                db.refresh(existing_doc)
                doc_id = existing_doc.id
                logger.info(f"Updating existing document: {item['title']} ({doc_id})")
            else:
                doc = Document(
                    id=uuid.uuid4(),
                    title=item["title"],
                    file_name=item["file_name"],
                    file_type="md",
                    storage_path=str(file_path),
                    category=item["category"],
                    department=item["department"],
                    academic_year=item["academic_year"],
                    processing_status=ProcessingStatus.UPLOADED,
                    version=1,
                    uploaded_by=admin_user.id,
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                doc_id = doc.id
                logger.info(f"Created new document record: {item['title']} ({doc_id})")

            # Execute Ingestion Pipeline
            success = ingest_document_sync(doc_id)
            if success:
                ingested_count += 1
                chunk_count = db.scalar(select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc_id)) or 0
                total_chunks += chunk_count
                logger.info(f"✓ Processed {item['title']}: {chunk_count} chunks embedded into pgvector.")
            else:
                logger.error(f"✗ Failed processing {item['title']}")

        logger.info(f"\n==========================================")
        logger.info(f"DEMO IMPORT COMPLETE:")
        logger.info(f"  Documents Ingested: {ingested_count}/{len(DEMO_DOCUMENTS)}")
        logger.info(f"  Total Chunks Created: {total_chunks}")
        logger.info(f"==========================================")


if __name__ == "__main__":
    run()
