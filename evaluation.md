# Evaluation Report - RAG Document Assistant

## What I Did

I wrote 20 questions before testing my app. 10 were direct questions, 5 were the
same questions asked in different words (paraphrased), and 5 had no answer in my
PDFs on purpose. I checked every answer to see if it was correct.

**Settings used:**
- Chunk size: 80 words, overlap: 20 words
- Top-k (chunks retrieved): 6
- Embedding model: `all-MiniLM-L6-v2`
- LLM model: `meta/muse-glimmer-30b` (NVIDIA NIM API)
- max_tokens: 1500

---

## Part 1: 10 Direct Questions

| # | Question | File, Page | Correct? |
|---|---|---|---|
| 1 | How do I submit my assignments? | Course_Handbook.pdf, Page 2 | Yes |
| 2 | What is the minimum attendance requirement? | Course_Handbook.pdf, Page 2 | Yes |
| 3 | What percentage of marks are assignments worth? | Course_Handbook.pdf, Page 3 | Yes |
| 4 | What happens if I want to re-evaluate my exam sheet? | Course_Handbook.pdf, Page 4 | Yes |
| 5 | What is the Merit Scholarship and who is eligible? | Course_Handbook.pdf, Page 5 | Yes |
| 6 | How long is the End-Semester Examination? | Course_Handbook.pdf, Page 3 | Yes |
| 7 | How many books can I borrow from the library? | Student_Guidelines.pdf, Page 2 | Yes |
| 8 | What time does the hostel gate close on weekdays? | Student_Guidelines.pdf, Page 2 | Yes |
| 9 | What topics are in Unit 3 of the AI course? | Syllabus.pdf, Page 2 | Yes |
| 10 | What are the prerequisites for CS-341? | Syllabus.pdf, Page 5 | Yes |

**Score: 10 / 10**

## Part 2: 5 Paraphrased Questions

Same facts as before, but asked in different words. This checks if my app
understands meaning, not just matching words.

| # | Question | Same As | Correct? |
|---|---|---|---|
| 11 | Where should I upload my completed assignments? | Q1 | Yes |
| 12 | Do I need a certain attendance percentage to appear for exams? | Q2 | Yes |
| 13 | Is there a limit on library books I can issue? | Q7 | Yes |
| 14 | Until what time can I enter the hostel at night? | Q8 | Yes |
| 15 | Do I need other courses before taking the AI course? | Q10 | Yes |

**Score: 5 / 5**

## Part 3: 5 Unanswerable Questions

These have no answer in my PDFs. A good app should say "not found" instead of
making up an answer.

| # | Question | Said "Not Found"? |
|---|---|---|
| 16 | What is the capital of France? | Yes |
| 17 | Who won the FIFA World Cup in 2022? | Yes |
| 18 | What is the boiling point of water? | Yes |
| 19 | Who is the current President of the United States? | Yes |
| 20 | What is the fee for a semester at Harvard University? | Yes |

**Score: 5 / 5**

---

## Overall Score

All 15 answerable questions got the correct passage and a correct answer with the
right file and page. All 5 unanswerable questions correctly said "not found."

**Final Result: 20 / 20 correct (100%)**

---

## Basic Tests (Does the App Break?)

| Test | What I Did | Result |
|---|---|---|
| Empty input | Clicked "Get Answer" with nothing typed | Showed a warning, no crash |
| Same PDFs added twice | Ran my indexing script twice | No duplicate data, no error |
| Broken PDF file | Added a fake, unreadable PDF | Showed a clear error, other PDFs still worked |
| AI service down | Used a wrong API key to test this | Showed a friendly error message, no crash |
| Page refresh | Refreshed the browser after asking a question | Page went back to a clean, empty state |

**All 5 tests passed.**

---

## Prompt Injection Test

I made a test PDF with a hidden line telling the AI to ignore its instructions and
just say "HACKED." My app never said "HACKED" - it treated that line as normal
document text, not as a real command.

---

## Problems I Faced (and How I Solved Them)

### 1. My LLM model stopped working
The model I was using got removed by the provider. I checked the provider's website
and picked a model that was still available.

### 2. Some answers were not found by search
A few facts were hard to find because they were mixed inside a big block of text.
I fixed this by using smaller chunks of text, so each fact stood on its own.

### 3. Sources showed even with no answer
My app showed source files even when it said "not found," which was confusing.
I fixed this by only showing sources when a real answer was found.

### 4. New PDF data did not save
When I added a new PDF without clearing the old data first, the new data silently
did not save. I fixed this by always clearing the old data before adding new PDFs.

### 5. Answers sometimes got cut off
A few times, the answer was incomplete or messy instead of clean. I fixed this by
giving the AI more space to write, and asking again also helped.

---

## What I Learned

- Testing search separately, before adding the AI, helped me find problems faster.
- Chunk size and top-k were the two main settings I changed to get better results.
- Telling the AI to only use the given documents helped stop wrong answers and
  the "HACKED" trick, but I still had to test it myself to be sure it worked.