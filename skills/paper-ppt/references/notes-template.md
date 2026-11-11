# Speaker Notes Template

Write one coherent paragraph per slide in the user's requested language or language mix. Do not force Chinese, English, or any other language when the user asks for something else. Keep the notes suitable for oral reporting rather than a list of fragments.

If the user does not specify a language, use the language of the latest request. If the requested language is ambiguous, ask before drafting.

## Problem slide

Explain the concrete failure mode or research gap, why common success metrics or prior reasoning do not cover it, and the question the paper addresses.

## Method slide

Follow the figure's data flow: inputs, modules, intermediate representations, decisions, outputs, and feedback. If the paper trains a model, state data sources, labels, architecture, frozen/fine-tuned parts, and loss functions.

## Experiment slide

State the environment, system, task difficulty, baselines, and run count before explaining each metric's meaning, unit, denominator, and direction of improvement. State only conclusions supported by the figures and tables.

## Results and boundary slide

Use the original qualitative figure to explain the mechanism, use ablations or tables to identify which component changes the result, and separate verified claims from untested limitations.
