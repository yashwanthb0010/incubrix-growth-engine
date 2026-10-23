# Real-Audience Preference Test Protocol
**Project:** IncuBrix Social Media Content Engine | **Target Sample:** 20+ Digital Creators & Marketers

## 1. Study Objective
Evaluate target audience preference, perceived usefulness, and click intent across AI-generated multi-platform social assets (LinkedIn educational posts, Instagram carousels, YouTube Shorts video scripts) derived from long-form content.

## 2. Participant Recruitment Criteria
Participants must meet at least 2 of the following 4 criteria:
1. Actively produces content on at least 1 social platform (LinkedIn, Instagram, YouTube, X, Substack).
2. Manages social accounts for a brand, startup, agency, or personal brand.
3. Spends 5+ hours weekly on content creation or marketing operations.
4. Has actively tested or currently uses at least one content tool (e.g. Canva, Opus Clip, Descript, Buffer, Notion).

## 3. Informed Consent & Privacy Statement
> "Participation in this assessment study is entirely voluntary. All answers are collected anonymously for academic and hiring assessment research. No personally identifiable information (PII), social credentials, or confidential business data is collected, stored, or distributed. You may exit the survey at any point."

## 4. Test Instrument (5 Evaluated Asset Pairs)
Participants are shown 5 paired asset variants (Variant A: Raw direct excerpt vs. Variant B: IncuBrix platform-optimized asset with structured hook, micro-lesson, and verified CTA).

### Survey Questions (5-point Likert Scale & Forced Choice):
1. **Hook Strength:** Which variant grabs your attention faster within the first 3 seconds? (Variant A / Variant B / Neutral)
2. **Perceived Educational Value:** Rate the actionable value of the content (1 = Low, 5 = High).
3. **Save/Bookmark Likelihood:** Would you save this post for future reference? (Yes / Maybe / No)
4. **Click-Through Intent:** Would you click the verified link to explore the complete workflow? (1 = Definitely Not, 5 = Highly Likely)
5. **Format Suitability:** Does the visual pacing / carousel structure feel native to the designated platform? (1 to 5)

## 5. Execution Protocol and Integrity Rules
- In accordance with the assessment brief: **Never fabricate survey responses or participants.**
- If 20 live external survey respondents have not completed the test at evaluation time, the report explicitly registers the actual status as `IN_PROGRESS` or `PARTIAL`, documenting the exact number of responses collected rather than faking data.
- The analysis script (`analyze_survey.py`) computes descriptive statistics, preference percentages, and statistical confidence intervals whenever CSV rows are loaded.
