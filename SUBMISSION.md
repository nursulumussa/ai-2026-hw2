HW2 submission
Name: Musa Nursulu
Student ID: S23067665
Group: 9
Repository: https://github.com/nursulumussa/ai-2026-hw2.git
AI tool disclosure
I used ChatGPT (OpenAI) to help draft the Python scripts for all three sublabs, set up the environment, troubleshoot API errors, and organize this submission. In Easy, AI helped draft the four role prompts (policy_officer, front_desk, auditor, and bilingual_clerk). I ran the scripts with my OpenAI API key and reported the observed results, rather than inventing outputs. I reviewed the written analysis based on those runs. The model used by the scripts should be verified in the MODEL constants before submission.
Sublab Easy — one task, four roles
Decisions per role
Each cell shows decision (Y/N = full agreement with the expected four fields).
Enquiry	policy_officer	front_desk	auditor	bilingual_clerk
E-01	granted (Y)	granted (Y)	more_info (N)	granted (Y)
E-02	refused (N)	more_info (Y)	more_info (Y)	refused (N)
E-03	refused (Y)	more_info (N)	refused (Y)	refused (Y)
E-04	refused (Y)	more_info (N)	refused (Y)	refused (Y)
E-05	granted (Y)	granted (Y)	more_info (N)	granted (Y)
E-06	granted (Y)	granted (Y)	more_info (N)	granted (Y)
E-07	granted (Y)	granted (Y)	more_info (N)	granted (Y)
E-08	not_found (Y)	not_found (Y)	not_found (Y)	not_found (Y)
E-09	refused (Y)	more_info (N)	refused (Y)	refused (Y)
E-10	more_info (Y)	more_info (Y)	more_info (Y)	refused (N)
agrees with expected	9/10	7/10	6/10	8/10
parsed	10/10	10/10	10/10	10/10
schema-valid	10/10	10/10	10/10	10/10


Which field moved, on which enquiry, under which role
Field	Enquiries that moved	Role(s) that moved it
found	none	none
decision	E-01, E-02, E-03, E-04, E-05, E-06, E-07, E-09, E-10	E-01: auditor; E-02: front_desk, auditor; E-03: front_desk; E-04: front_desk; E-05: auditor; E-06: auditor; E-07: auditor; E-09: front_desk; E-10: bilingual_clerk
amount	E-07	auditor
missing_documents	none	none


Raw replies
Full JSON reply for E-02 from front_desk, where the decision differs from the policy officer:
[PASTE EXACT CONTENT OF easy_results.json -> front_desk -> E-02 -> raw HERE]
Full JSON reply for E-07 from bilingual_clerk (retain the Kazakh-language reason):
[PASTE EXACT CONTENT OF easy_results.json -> bilingual_clerk -> E-07 -> raw HERE]
Written answers
1. Which fields are role-sensitive and which are not?
decision is most role-sensitive: nine enquiries show at least one difference from the policy officer. amount also changed once (E-07 under auditor). found and missing_documents did not change in any comparison. This suggests that role wording affected decisions more than factual retrieval.
2. Which enquiries are most sensitive to the role, and why those?
E-03 and E-04 show the difference between a strict policy officer and a front-desk role that prefers more_info instead of refusal. E-07 is the Kazakh-language enquiry; the bilingual clerk kept the policy officer's decision, while the auditor changed it to more_info and changed the amount. E-10 tests what happens when an ID card is missing: the policy officer requested more information, but the bilingual clerk refused. These rows expose role influence on how policy, missing documentation, and language are handled.
3. Where does discretion belong — the role paragraph, or code that reads decision afterwards?
A role paragraph can change how the model explains a case, but final eligibility should be checked in deterministic code against the policy and authoritative records. A downstream program receiving just the JSON decision cannot reliably infer which role generated it, because the same output schema is used by all roles. The role should be recorded as separate trusted metadata if it matters.
4. Is a role a boundary?
No. A role paragraph is prompt text, not a security or correctness boundary. I would enforce permitted decisions, award amounts, required documents, and policy constraints in code and validate the output schema. For expensive mistakes I would also verify each decision against official records and trigger human review for uncertainty.
Sublab Medium — memory you choose
Tokens per call
Call	A — never compressed	B — compressed at the compress turn
1	62	62
2	122	131
3	207	233
4	302	334
5	398	420
6	506	558
7	625	665
8	735	782
9	835	882
10	943	306
11	1103	456
12	N/A — not run	N/A — not run
peak	1103	882
total for the run	5838	4829


The supplied run contained 11 calls, not 12. The values above report the actual run rather than inventing a twelfth call.
Probes after the conversation
Probe	Tests	A retrieved?	A answer	B retrieved?	B answer
Q-1 identity	turn 1	Yes	Daniyar Qoshan, A-202	Yes	Daniyar Qoshan, A-202
Q-2 missing document	turn 5	Yes	ID card; delivery planned Thursday, not confirmed	Yes	ID card copy or scan
Q-3 band and amount	turns 3–4	No	Income band 2 reported; grant amount unconfirmed	No	Income band 2; grant amount unconfirmed
Q-4 the constraint	turn 6	Yes	Can visit on Thursdays	Yes	Can visit on Thursdays
Q-5 the open question	turn 7	Yes	Whether employer-letter scan is acceptable instead of original	Yes	Whether employer-letter scan is acceptable instead of original
retrieved		4/5		4/5	


The state my compression produced
{
  "applicant_id": "A-202",
  "topic": "Study grant application eligibility, document submission, award amount, and family application records",
  "facts": [
    "The applicant's name is Daniyar Qoshan.",
    "The applicant sent their transcript last week.",
    "The applicant's income band is 2 according to their family's certificate.",
    "The applicant could not upload their ID card because the scanner at home broke.",
    "The applicant's sister Aruzhan applied last year and is on file."
  ],
  "decisions": [],
  "constraints": [
    "The applicant can only come to the office on Thursdays.",
    "The applicant has lab all week otherwise.",
    "The applicant cannot currently scan the ID card at home because the scanner is broken."
  ],
  "open_questions": [
    "Does a scanned letter from the applicant's employer count, or is the original required?",
    "If the applicant brings the ID card on Thursday, will the decision be made the same day?",
    "Does the applicant qualify for the study grant?",
    "How much would the grant amount be if approved?",
    "Does Aruzhan's previous application affect application A-202?"
  ],
  "language": "English with some Kazakh"
}
Written answers
1. What did compression buy?
Compression reduced the peak prompt-token count from 1103 to 882 (221 fewer, about 20.0%) and the total from 5838 to 4829 (1009 fewer, about 17.3%). Both modes retrieved 4/5 probes. Q-3, based on turns 3–4, failed the retrieval check in both modes. The answers mention income band 2, but do not establish a grant amount; that may explain the failed check. Compression did not create an additional measured loss in this run.
2. Why must the state be structured rather than a paragraph?
Named fields separate identity, facts, constraints, decisions, and unresolved questions. Code can check whether a required field is present and pass only the necessary facts to later requests. A free-form summary is harder to validate and may mix confirmed information with questions or assumptions.
3. What is missing from your state that you would add?
I would add a verification_status field for income band and documents, plus a source turn or timestamp for each important fact. To control token use, I would remove redundant details from constraints, such as repeating the broken-scanner explanation already present in facts.
4. When is compression the wrong choice?
Compression is risky for legal, medical, or financial conversations where exact wording, chronology, or a minor exception matters. A compressed state could silently omit a disclaimer or a change of decision. This program tests five probes, but it would not detect every possible omitted detail. Critical original messages should be retained in a separate auditable log.
Sublab Hard — stories in, CVs out, the best candidate by code
Part 1 — extraction
Story	Parsed?	Valid?	Fields that came back null	Traps hit
story-01	Yes	Yes	none	No listed trap
story-02	Yes	Yes	graduation_year, gpa_4_scale, gpa_original_scale, published_peer_reviewed_outputs	No GPA stated; publication's peer-review status unverified
story-03	Yes	Yes	none	GPA on 5.0 scale; paper under review not counted
story-04	Yes	Yes	none	Papers under review / in preparation not counted
story-05	Yes	Yes	none	Unpublished paper not counted; Kazakh-language story
story-06	Yes	Yes	graduation_year, gpa_4_scale, gpa_original_scale	Contradictory graduation year and GPA; grading scale absent


Extraction for story-06 (from the actual run):
{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_4_scale": null,
  "gpa_original_scale": null,
  "languages": ["Kazakh", "Russian", "English"],
  "published_peer_reviewed_outputs": 1,
  "relevant_experience_months": 40,
  "evidence": {
    "candidate_id": "story-06",
    "full_name": "# Nurzhan Abilov",
    "degree": "I graduated in 2024 with a BSc in Statistics.",
    "graduation_year": "I graduated in 2024 with a BSc in Statistics. ... I am currently a final-year student graduating in 2026",
    "gpa_4_scale": "My GPA was 3.2. Actually I should double-check that, I think it was 3.5",
    "gpa_original_scale": null,
    "languages": "Languages: Kazakh, Russian, English.",
    "published_peer_reviewed_outputs": "one paper published, in a peer-reviewed proceedings, on survey weighting.",
    "relevant_experience_months": "I have been at an insurance analytics team since February 2023, which is about forty months.",
    "unpublished_papers": "One poster at a local event, which I do not think counts."
  },
  "ambiguities": [
    "Graduation year is contradictory: the candidate states both 2024 and 2026.",
    "GPA is contradictory and unverified: both 3.2 and 3.5 are stated, and the candidate says the number should be double-checked.",
    "The original GPA scale is not stated, so no conversion to a 4.0 scale is possible.",
    "Relevant experience is stated as approximately forty months; the first eight months were part-time, but the candidate describes continuous employment."
  ],
  "unpublished_papers": []
}
Part 2 — scores and the winner
Candidate	academic (0–5)	research (0–5)	experience (0–5)	weighted total (code)
story-01	5	5	2	4.40
story-02	0	0	5	1.00
story-03	4	2.5	3	3.35
story-04	4	2	5	3.60
story-05	5	3	1	3.60
story-06	0	2.5	5	1.75


Winner, computed by my code: story-01 — Aziza Bekova (4.40).
The model's prose answer, asked separately ("who should win?"):
Aziza Bekova should receive the scholarship. She has a strong 3.8/4.0 GPA and is the only candidate with two confirmed published peer-reviewed outputs, which together carry 80% of the rubric’s weight. Although her relevant experience is limited to eight months, this is outweighed by her academic and research record. Tamerlan Saparov has longer experience, but his lower GPA and single publication make Aziza the strongest overall choice.

Part 3 — written answers
1. Which rule did you have to add, and what broke without it?
The extraction needed a rule to count only confirmed, published, peer-reviewed work. Story-03 has an article under review, and story-04 lists several papers that are not published. Without this rule, counting any mentioned paper would inflate research scores. Story-02 also demonstrates why a conference paper with unspecified peer-review status cannot automatically be counted as peer-reviewed.
2. Where did the model guess, and where did your code have to decide?
The model interpreted approximate experience in story-06 as 40 months even though the story mentioned part-time work and called the duration approximate; this needs verification. Code then applied the fixed rubric and weights to extracted fields rather than allowing the model to invent a total or winner. It also treated missing GPA as an academic score of zero under the implemented scoring rule.
3. Did your prose ranking and your computed ranking agree?
Yes. Both selected Aziza Bekova (story-01). I trust the computed ranking more because the formula and inputs can be inspected and reproduced. Before relying on the prose recommendation alone, I would need evidence that it consistently applies the same weights, handles missing data, and reaches the same decision on challenging and conflicting examples.
4. The rubric has no anchor for a contradicted field.
In story-06 the GPA appears as 3.2 and then 3.5, with no reliable grading scale. The extraction returned null, and the code scored the academic component as 0 under the current implementation. A clearer policy should distinguish missing or contradictory evidence from proven low performance: mark the GPA unverified, request clarification, and either pause ranking or use a published provisional-scoring rule consistently across applicants. A zero here is a policy choice, not proof of a low GPA.
5. How close were your top two candidates?
The winner scored 4.40 and the next-ranked candidates scored 3.60 (a tie between story-04 and story-05). The gap is 0.80, not within 0.05. I would still check the source evidence and rubric calculations before making a final decision. If the candidates had been within 0.05, I would recommend manual review and extraction that records precise citations and verification status for each scored fact.
Reflection (optional, one short paragraph)
Next time I build an application using structured model output, I will define the JSON schema first, validate each answer in code, and separate model extraction from deterministic policy decisions. I will keep source evidence and uncertainty visible instead of allowing the model to fill in missing facts. For long conversations, I will use structured compression only when the original messages remain available for auditing.
Before submitting — complete these checks
- Replace the four personal/repository placeholders at the top.
- Insert the two actual Easy raw JSON replies, including reason, from easy_results.json.
- Check the required call count: the provided Medium run had 11 calls, while this template has 12 rows. Follow the instructor's exact requirements if 12 are mandatory.
- Review the extracted fields against data/cv_stories and the grading rubric, especially ambiguous papers, GPA conversion, and contradictory details.
- Confirm .env and API keys are excluded from Git (.gitignore).
- If you copied AI-written answers, read them and adjust to reflect what you understand and actually did.