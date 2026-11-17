# Experiment 1 results summary

Logistic regression (standardized relative delta, theta, alpha and beta power) trained on Task 1 and tested once on Task 2.

## Primary analysis (frozen 110-participant preprocessing)
Test ROC-AUC = 0.476 (95% bootstrap CI 0.262–0.684; train n = 75, test n = 35: 14 controls, 21 psychosis). The interval includes 0.50, so these data do not show convincing above-chance discrimination. At threshold 0.50: accuracy 0.571, sensitivity 0.810, specificity 0.214, F1 0.694 (TN 3, FP 11, FN 4, TP 17).

## Sensitivity analysis (original 107-participant preprocessing)
Test ROC-AUC = 0.485 (95% bootstrap CI 0.267–0.684; train n = 74, test n = 33: 14 controls, 19 psychosis). The interval includes 0.50, so these data do not show convincing above-chance discrimination. At threshold 0.50: accuracy 0.606, sensitivity 0.789, specificity 0.357, F1 0.698 (TN 5, FP 9, FN 4, TP 15).

The two versions lead to the same conclusion about whether the interval includes 0.50.
Training and test samples both differ between versions, so a difference cannot be attributed only to channel omission. The 110-participant version remains the primary analysis.

## Limitations
- The CI reflects test-sample uncertainty for the fitted model only, not training-sample uncertainty.
- Threshold metrics should be compared with always predicting psychosis (Task 2 majority class: accuracy 0.600). The primary model predicted psychosis for 28 of 35 participants, consistent with the Task 1 class balance and no class weighting.
- Small test set (35 participants), and uneven exclusions (Task 1 8.5%, Task 2 42.6%), so retained participants may not represent the full cohorts.
- Three recovered participants use 48 channels (one isolated bad channel omitted) instead of 49.
- No shared IDs, but person-level independence of the two datasets is unconfirmed; Task 1 includes ten acquisition-2 participants.
- The four relative powers sum to one, so coefficients are not independent biological effects.
- This is a research analysis, not a clinically validated diagnostic tool.
