## Task Description

Analyze the uploaded exam papers given in the sources and extract questions based on the chapter structure in the provided syllabus in "Syllabus.pdf". Separate theoretical questions from practical problems, and create a dedicated section for short note questions. Count how many times each question pattern appears across all exam papers.

## Instructions

1. Follow the exact chapter/topic structure from the provided syllabus
2. For each chapter/topic:
   - First list all theoretical questions (definitions, explanations, derivations, concepts)
   - Then list all practical/numerical problems separately
   - Ensure questions are placed in their correct chapter according to subject taxonomy
3. Create a separate "Short Notes" section at the end that collects all short note questions
4. Count frequency of each question type/pattern
5. If a question spans multiple topics, place it under the primary topic it addresses
6. For questions containing or referencing visual elements:
   - Include the text of the question as is
   - Add a note in parentheses indicating which paper contains the visual element
   - Look for both explicit references (e.g., "shown in figure") and implicit references (e.g., "the diagram below", "as shown", "the given table", etc.)
   - For questions with tables, graphs, or any visual data necessary to solve the problem, add a note to check the original paper
   - Example: "Analyze the circuit shown in the figure. (See Spring 2020 Question 2a for the figure)"
   - Example: "Interpret the data presented in the graph. (See Fall 2019 Question 3c for the graph)"
7. Implete proper numbering system for the lists (use only integer number system for all heading, subheading, and question list.)

## Output Format

```
**CHAPTER/TOPIC X: [NAME]**

## THEORETICAL QUESTIONS
* **[SUBTOPIC NAME]**: Asked N times
    * [List of theoretical questions]
    * [List concept/derivation questions]

* **[NEXT SUBTOPIC]**: Asked M times
    * [List of theoretical questions]

## PRACTICAL/NUMERICAL PROBLEMS
* **[SUBTOPIC NAME]**: Asked P times
    * [List of practical problems with their exact wording]
    * [List similar problems with reference to figures if needed]

**CHAPTER/TOPIC X+1: [NEXT NAME]**
...

**SHORT NOTES SECTION**
* **[TOPIC 1]**: Asked Q times
    * Write short notes on: [Topic 1]

* **[TOPIC 2]**: Asked R times
    * Write short notes on: [Topic 2]
```

## Important Classification Rules

- Questions must be placed in their most appropriate chapter/topic according to the syllabus
- Questions asking to "explain", "define", "describe", or "derive" should be classified as theoretical questions
- Questions with calculations, applications, or practical implementations should be classified as practical/numerical problems
- Questions asking for "short notes" should be placed in the dedicated Short Notes section
- Use the subject's taxonomy to determine the correct placement of cross-disciplinary questions

## Important Requirements

- DO NOT add any explanations, formulas, or content beyond the exact question wording
- ONLY categorize and count questions - do not provide study material or explanations
- Maintain the exact hierarchical structure from the syllabus
- Count questions precisely - a question is counted multiple times if it appears in different papers
- Include all variations of similar questions
- Group questions by conceptual similarity, not just identical wording
- For questions that reference figures, diagrams, or tables, include a specific reference to the original exam paper and question number in parentheses
- Be alert for phrases like "below", "given", "shown", "depicted", "illustrated", which often indicate the presence of a figure or diagram in the original question paper

## Analysis Tips

- Identify subject-specific keywords that indicate which chapter/topic a question belongs to
- Pay attention to the type of task requested (explain, calculate, analyze, etc.) to properly categorize questions
- Look for subject-specific terminology that helps place questions in the correct section
- Recognize common question patterns within the discipline to group similar questions together
