
#!/usr/bin/env python3
"""
Script to populate the database with sample job roles across various departments
"""

from core.database import DatabaseManager

def populate_sample_roles():
    """Add comprehensive job roles to the database"""
    db = DatabaseManager()
    
    # Sample roles data
    sample_roles = [
        # Software Engineering
        {
            "title": "Software Engineer I",
            "department": "Engineering",
            "level": "Entry Level",
            "description": "Develop and maintain software applications. Write clean, efficient code following best practices. Collaborate with team members on feature development and bug fixes. Participate in code reviews and testing processes.",
            "skills": "Python, JavaScript, Git, SQL, Problem Solving, Debugging, Unit Testing, Agile"
        },
        {
            "title": "Senior Software Engineer",
            "department": "Engineering", 
            "level": "Senior Level",
            "description": "Lead development of complex software systems. Mentor junior developers and provide technical guidance. Design system architecture and make technology decisions. Drive technical excellence and best practices.",
            "skills": "Advanced Programming, System Design, Architecture, Leadership, Mentoring, Code Review, Performance Optimization"
        },
        {
            "title": "Full Stack Developer",
            "department": "Engineering",
            "level": "Mid Level", 
            "description": "Develop both frontend and backend components of web applications. Work with databases, APIs, and user interfaces. Ensure seamless integration between different system components.",
            "skills": "React, Node.js, Python, MongoDB, PostgreSQL, REST APIs, HTML/CSS, DevOps"
        },
        {
            "title": "DevOps Engineer",
            "department": "Engineering",
            "level": "Mid Level",
            "description": "Manage deployment pipelines and infrastructure automation. Monitor system performance and ensure scalability. Implement CI/CD processes and maintain cloud environments.",
            "skills": "AWS, Docker, Kubernetes, Jenkins, Terraform, Linux, Python, Monitoring, CI/CD"
        },
        {
            "title": "Engineering Manager",
            "department": "Engineering",
            "level": "Management",
            "description": "Lead and manage engineering teams. Set technical direction and ensure project delivery. Conduct performance reviews and career development for team members. Bridge technical and business requirements.",
            "skills": "Leadership, Project Management, Technical Strategy, People Management, Agile, Communication"
        },
        
        # Data Science & Analytics
        {
            "title": "Data Analyst",
            "department": "Data",
            "level": "Entry Level",
            "description": "Analyze data to provide business insights. Create reports and dashboards. Work with stakeholders to understand data requirements and translate findings into actionable recommendations.",
            "skills": "SQL, Excel, Python, Data Visualization, Statistics, Tableau, PowerBI, Communication"
        },
        {
            "title": "Data Scientist",
            "department": "Data",
            "level": "Mid Level",
            "description": "Build predictive models and machine learning solutions. Conduct advanced statistical analysis. Design experiments and interpret complex data patterns to drive business decisions.",
            "skills": "Python, R, Machine Learning, Statistics, SQL, TensorFlow, scikit-learn, Data Mining"
        },
        {
            "title": "Senior Data Scientist",
            "department": "Data",
            "level": "Senior Level",
            "description": "Lead data science initiatives and complex modeling projects. Mentor junior data scientists. Design data science strategy and establish best practices for the team.",
            "skills": "Advanced ML, Deep Learning, Model Deployment, Leadership, Research, MLOps, Big Data"
        },
        {
            "title": "Machine Learning Engineer",
            "department": "Data",
            "level": "Mid Level",
            "description": "Deploy and maintain machine learning models in production. Build ML pipelines and infrastructure. Optimize model performance and ensure scalability of ML systems.",
            "skills": "MLOps, Python, TensorFlow, PyTorch, Kubernetes, AWS, Model Deployment, Data Engineering"
        },
        
        # Product Management
        {
            "title": "Associate Product Manager",
            "department": "Product",
            "level": "Entry Level",
            "description": "Support product development initiatives. Conduct market research and user analysis. Assist in product roadmap planning and feature prioritization under senior guidance.",
            "skills": "Product Strategy, User Research, Analytics, Communication, Project Management, Agile"
        },
        {
            "title": "Product Manager",
            "department": "Product",
            "level": "Mid Level",
            "description": "Own product vision and strategy for specific features or products. Work with cross-functional teams to deliver products. Analyze user feedback and market trends to drive product decisions.",
            "skills": "Product Strategy, Roadmapping, User Research, Analytics, Stakeholder Management, Agile"
        },
        {
            "title": "Senior Product Manager",
            "department": "Product",
            "level": "Senior Level",
            "description": "Lead product strategy for major product lines. Drive product vision and coordinate with multiple teams. Mentor junior PMs and establish product best practices.",
            "skills": "Strategic Planning, Leadership, Market Analysis, User Experience, Data Analysis, Cross-functional Leadership"
        },
        {
            "title": "Product Owner",
            "department": "Product",
            "level": "Mid Level",
            "description": "Manage product backlog and define user stories. Work closely with development teams in agile environment. Ensure product features meet business requirements and user needs.",
            "skills": "Agile, Scrum, User Stories, Backlog Management, Stakeholder Communication, Requirements Analysis"
        },
        
        # Marketing
        {
            "title": "Digital Marketing Specialist",
            "department": "Marketing",
            "level": "Entry Level",
            "description": "Execute digital marketing campaigns across various channels. Manage social media presence and create marketing content. Analyze campaign performance and optimize for better results.",
            "skills": "Digital Marketing, Social Media, Content Creation, Google Analytics, SEO, Email Marketing"
        },
        {
            "title": "Marketing Manager",
            "department": "Marketing",
            "level": "Mid Level",
            "description": "Develop and execute marketing strategies. Manage marketing campaigns and budgets. Coordinate with sales teams and analyze market trends to identify opportunities.",
            "skills": "Marketing Strategy, Campaign Management, Budget Management, Analytics, Leadership, Communication"
        },
        {
            "title": "Content Marketing Manager",
            "department": "Marketing",
            "level": "Mid Level",
            "description": "Create and manage content marketing strategy. Oversee blog, social media, and other content channels. Collaborate with design and product teams to create compelling content.",
            "skills": "Content Strategy, Writing, SEO, Social Media, Analytics, Creative Direction, Brand Management"
        },
        {
            "title": "Growth Marketing Manager",
            "department": "Marketing",
            "level": "Senior Level",
            "description": "Drive user acquisition and retention strategies. Design and execute growth experiments. Analyze user behavior and optimize conversion funnels for sustainable growth.",
            "skills": "Growth Hacking, A/B Testing, Analytics, User Acquisition, Retention, Data Analysis, Experimentation"
        },
        
        # Sales
        {
            "title": "Sales Development Representative",
            "department": "Sales",
            "level": "Entry Level",
            "description": "Generate leads and qualify prospects. Conduct initial outreach and schedule meetings for account executives. Maintain CRM records and support sales pipeline development.",
            "skills": "Lead Generation, Communication, CRM, Cold Calling, Email Marketing, Prospecting"
        },
        {
            "title": "Account Executive",
            "department": "Sales",
            "level": "Mid Level",
            "description": "Manage sales process from lead to close. Build relationships with prospects and customers. Present product demos and negotiate contracts to meet sales targets.",
            "skills": "Sales Process, Relationship Building, Negotiation, Presentation, CRM, Communication"
        },
        {
            "title": "Senior Account Executive",
            "department": "Sales",
            "level": "Senior Level",
            "description": "Handle enterprise accounts and complex sales cycles. Mentor junior sales staff and develop sales strategies. Collaborate with customer success to ensure client satisfaction.",
            "skills": "Enterprise Sales, Strategic Selling, Leadership, Account Management, Negotiation, Customer Success"
        },
        {
            "title": "Sales Manager",
            "department": "Sales",
            "level": "Management",
            "description": "Lead and manage sales team performance. Set sales targets and develop strategies to achieve revenue goals. Conduct training and performance reviews for sales staff.",
            "skills": "Sales Leadership, Team Management, Revenue Planning, Performance Management, Coaching, Strategy"
        },
        
        # Customer Success
        {
            "title": "Customer Success Representative",
            "department": "Customer Success",
            "level": "Entry Level", 
            "description": "Support customer onboarding and adoption. Respond to customer inquiries and provide product assistance. Monitor customer health scores and identify at-risk accounts.",
            "skills": "Customer Service, Communication, Problem Solving, Product Knowledge, CRM, Empathy"
        },
        {
            "title": "Customer Success Manager",
            "department": "Customer Success",
            "level": "Mid Level",
            "description": "Manage customer relationships and ensure success with product adoption. Drive customer retention and expansion opportunities. Coordinate with product and support teams.",
            "skills": "Account Management, Customer Retention, Relationship Building, Analytics, Communication, Strategy"
        },
        
        # Human Resources
        {
            "title": "HR Generalist",
            "department": "Human Resources",
            "level": "Mid Level",
            "description": "Support various HR functions including recruitment, employee relations, and performance management. Assist with policy development and compliance. Handle employee inquiries and workplace issues.",
            "skills": "Recruitment, Employee Relations, HR Policies, Performance Management, Communication, Compliance"
        },
        {
            "title": "Talent Acquisition Specialist",
            "department": "Human Resources", 
            "level": "Mid Level",
            "description": "Lead recruitment efforts across multiple roles and departments. Source candidates, conduct interviews, and manage hiring process. Build talent pipeline and improve recruitment strategies.",
            "skills": "Recruitment, Interviewing, Sourcing, ATS, Candidate Assessment, Networking, Communication"
        },
        {
            "title": "HR Manager",
            "department": "Human Resources",
            "level": "Management",
            "description": "Oversee HR operations and strategy. Manage HR team and ensure compliance with employment laws. Drive employee engagement initiatives and organizational development.",
            "skills": "HR Strategy, Leadership, Compliance, Employee Engagement, Policy Development, Change Management"
        },
        
        # Finance
        {
            "title": "Financial Analyst",
            "department": "Finance",
            "level": "Entry Level",
            "description": "Perform financial analysis and prepare reports. Support budgeting and forecasting processes. Analyze financial data to provide insights for business decision-making.",
            "skills": "Financial Analysis, Excel, Financial Modeling, Budgeting, Reporting, Analytics, Communication"
        },
        {
            "title": "Senior Financial Analyst",
            "department": "Finance",
            "level": "Senior Level",
            "description": "Lead complex financial analysis projects. Develop financial models and forecasts. Present findings to senior management and support strategic planning initiatives.",
            "skills": "Advanced Financial Modeling, Strategic Analysis, Leadership, Presentation, Forecasting, Business Strategy"
        },
        {
            "title": "Accountant",
            "department": "Finance",
            "level": "Mid Level",
            "description": "Manage day-to-day accounting operations. Prepare financial statements and ensure compliance with accounting standards. Handle accounts payable, receivable, and general ledger entries.",
            "skills": "Accounting, Financial Reporting, GAAP, QuickBooks, Excel, Attention to Detail, Compliance"
        },
        {
            "title": "Finance Manager",
            "department": "Finance",
            "level": "Management", 
            "description": "Oversee financial operations and reporting. Manage finance team and ensure accurate financial records. Support strategic planning and business decision-making with financial insights.",
            "skills": "Financial Management, Leadership, Strategic Planning, Budgeting, Team Management, Compliance"
        },
        
        # Operations
        {
            "title": "Operations Coordinator",
            "department": "Operations",
            "level": "Entry Level",
            "description": "Support daily operations and administrative tasks. Coordinate between departments and manage operational processes. Assist with project management and process improvement initiatives.",
            "skills": "Operations Management, Communication, Organization, Process Improvement, Project Coordination, Multitasking"
        },
        {
            "title": "Business Operations Analyst",
            "department": "Operations",
            "level": "Mid Level",
            "description": "Analyze business processes and identify improvement opportunities. Create operational reports and metrics dashboards. Support cross-functional projects and process optimization.",
            "skills": "Process Analysis, Data Analysis, Project Management, Reporting, Communication, Problem Solving"
        },
        {
            "title": "Operations Manager",
            "department": "Operations",
            "level": "Management",
            "description": "Lead operational strategy and process optimization. Manage operations team and ensure efficient business processes. Drive operational excellence and continuous improvement initiatives.",
            "skills": "Operations Strategy, Leadership, Process Optimization, Team Management, Strategic Planning, Performance Management"
        },
        
        # Design
        {
            "title": "UX/UI Designer",
            "department": "Design",
            "level": "Mid Level",
            "description": "Design user interfaces and experiences for digital products. Conduct user research and create wireframes, prototypes, and visual designs. Collaborate with product and engineering teams.",
            "skills": "UI/UX Design, Figma, Adobe Creative Suite, User Research, Prototyping, Wireframing, Design Systems"
        },
        {
            "title": "Senior UX Designer",
            "department": "Design", 
            "level": "Senior Level",
            "description": "Lead UX design for complex products and features. Conduct advanced user research and usability testing. Establish design standards and mentor junior designers.",
            "skills": "Advanced UX Design, User Research, Usability Testing, Design Strategy, Leadership, Mentoring"
        },
        {
            "title": "Product Designer",
            "department": "Design",
            "level": "Mid Level",
            "description": "Own end-to-end product design from concept to implementation. Work closely with product managers and engineers. Balance user needs with business goals in design decisions.",
            "skills": "Product Design, User-Centered Design, Prototyping, Design Thinking, Collaboration, Problem Solving"
        },
        
        # Quality Assurance
        {
            "title": "QA Tester",
            "department": "Quality Assurance",
            "level": "Entry Level",
            "description": "Execute manual testing procedures and document bugs. Create and maintain test cases. Work with development teams to ensure product quality and user experience.",
            "skills": "Manual Testing, Bug Reporting, Test Case Design, Attention to Detail, Communication, Problem Solving"
        },
        {
            "title": "QA Engineer",
            "department": "Quality Assurance",
            "level": "Mid Level",
            "description": "Design and implement automated testing frameworks. Develop test strategies and ensure comprehensive test coverage. Lead quality assurance processes and mentor junior testers.",
            "skills": "Automated Testing, Test Automation, Selenium, Programming, Test Strategy, CI/CD, Quality Processes"
        },
        
        # Legal
        {
            "title": "Legal Counsel",
            "department": "Legal",
            "level": "Senior Level",
            "description": "Provide legal guidance on business operations and contracts. Review and negotiate agreements. Ensure compliance with regulations and manage legal risks for the organization.",
            "skills": "Legal Analysis, Contract Negotiation, Compliance, Risk Management, Communication, Business Law"
        },
        
        # Executive
        {
            "title": "Chief Technology Officer",
            "department": "Executive",
            "level": "Executive",
            "description": "Lead technology strategy and vision for the organization. Oversee engineering and technical teams. Drive innovation and ensure technical architecture supports business goals.",
            "skills": "Technology Strategy, Leadership, Innovation, Technical Vision, Team Management, Strategic Planning"
        },
        {
            "title": "Chief Product Officer",
            "department": "Executive", 
            "level": "Executive",
            "description": "Define product strategy and roadmap for the company. Lead product organization and drive product excellence. Ensure products meet market needs and business objectives.",
            "skills": "Product Strategy, Leadership, Market Analysis, Innovation, Strategic Planning, Team Management"
        }
    ]
    
    print("Adding sample roles to database...")
    
    # Add each role to the database
    for i, role in enumerate(sample_roles):
        try:
            role_id = db.save_job_role(
                title=role["title"],
                department=role["department"], 
                level=role["level"],
                description=role["description"],
                skills=role["skills"],
                file_path=f"sample_role_{i+1}.txt",
                uploaded_by=1  # Admin user ID
            )
            print(f"✅ Added: {role['title']} (ID: {role_id})")
            
        except Exception as e:
            print(f"❌ Error adding {role['title']}: {str(e)}")
    
    print(f"\n🎉 Successfully populated database with {len(sample_roles)} job roles!")
    print("\nRoles added across departments:")
    
    # Count roles by department
    dept_counts = {}
    for role in sample_roles:
        dept = role["department"]
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    for dept, count in dept_counts.items():
        print(f"  • {dept}: {count} roles")

if __name__ == "__main__":
    populate_sample_roles()
