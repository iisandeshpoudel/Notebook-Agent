# Meta-Prompt for Creating Subject-Specific Exam Analysis Prompts

## Task Definition

This meta-prompt guides the creation of a subject-specific exam analysis prompt by analyzing:

1. A subject syllabus (syllabus.md)
2. Initial output from the general prompt (output.md)
3. Any specific subject requirements

Your task is to create a refined, subject-specific prompt that enhances the general prompt with domain-specific guidance and classification rules.

## Instructions

1. Analyze the provided syllabus structure and identify:

   - Main chapters/topics and their hierarchical organization
   - Subject-specific terminology and concepts
   - The fundamental taxonomy of the subject
   - Types of problems typical to this field (theoretical vs. practical/numerical)

2. Review the initial output.md to identify:

   - Areas where questions could be better categorized
   - Subject-specific patterns that emerge
   - Common question types in this discipline
   - Issues with classification or organization

3. Create a refined prompt that includes:
   - Subject-specific classification rules
   - Keywords for identifying question types
   - Custom output formatting aligned with the subject's structure
   - Specific instructions for handling domain-specific visual elements
   - Enhanced analysis tips for the particular subject
   - Improved topic weightage analysis
   - Domain-specific difficulty indicators

## Refined Prompt Structure

Your refined prompt should include the following sections:

### 1. Task Description

Customize the task description to match the subject's terminology and question types.

### 2. Instructions

Adapt the general instructions with subject-specific directions about:

- Following the exact chapter structure from the syllabus
- Categorizing questions (theoretical vs. practical) using subject-appropriate terminology
- Handling cross-topic questions according to the subject's taxonomy
- Dealing with subject-specific visual elements (diagrams, charts, graphs, etc.)
- Any unique classification requirements for this field

### 3. Output Format

Preserve the general structure but customize terminology to match the subject:

- Use the exact chapter names from the syllabus
- Adjust subsection names to match subject terminology (e.g., "Theoretical Questions" might become "Proofs" for mathematics)
- Add subject-specific subsections if needed

### 4. Classification Rules

This is the most important section to customize:

- Create 5-10 specific rules for the subject (e.g., "All integration problems MUST be placed in Chapter X")
- Define what constitutes theoretical vs. practical problems in this specific subject
- Establish how to handle interdisciplinary questions
- Specify rules for classifying questions that use specific methodologies

### 5. Requirements

Enhance the general requirements with:

- Subject-specific guidelines for question grouping
- Domain-specific instructions for handling figures, diagrams, or special notation
- Additional documentation needs unique to the field

### 6. Analysis Tips

Create a comprehensive set of subject-specific keywords and phrases that help identify:

- Which chapter/topic a question belongs to
- The type of question (proof, calculation, analysis, etc.)
- Complexity indicators
- Standard problem types in the field

## Example Transformation

Here's how you might transform a general prompt segment for a Mathematics course:

**From General**:

```
- Questions asking to "explain", "define", "describe", or "derive" should be classified as theoretical questions
```

**To Mathematics-Specific**:

```
- Questions asking to "prove", "show that", "demonstrate", or "derive" should be classified as theoretical questions
- Questions involving "find", "calculate", "solve", "evaluate", or "compute" should be classified as practical problems
- All integration techniques must be placed in Chapter 4 (Techniques of Integration)
- All series convergence questions must be placed in Chapter 9 (Infinite Series)
```

## Process Guidelines

1. First identify the subject's unique structure and terminology
2. Map the general question types to subject-specific question types
3. Create subject-specific classification rules based on the syllabus
4. Develop a keyword mapping for chapters and question types
5. Enhance the analysis section with subject-specific patterns
6. Add topic weightage analysis tailored to the subject
7. Include domain-specific difficulty indicators

Your final product should be a refined prompt that:

- Speaks the language of the specific subject
- Provides clear classification guidance tailored to the field
- Helps properly organize questions according to the subject's taxonomy
- Identifies subject-specific patterns in the question data
- Preserves all the functionality of the general prompt while enhancing it with domain knowledge
