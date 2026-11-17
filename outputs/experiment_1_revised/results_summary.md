# Experiment 1 (revised) results summary

Revised exploratory analysis: Dataset 2 results had already been seen in the original Experiment 1, so this is not a first external validation.
Settings were chosen by 5-fold cross-validation within Dataset 1 only, saved, and then tested once on Dataset 2.

## Primary analysis (frozen 110-participant preprocessing)
Selected C = 0.1, class_weight = None. Dataset 2 ROC-AUC = 0.497 (95% CI 0.289–0.704; n = 35: 14 controls, 21 psychosis). The interval includes 0.50, so above-chance discrimination is not supported. At threshold 0.50: balanced accuracy 0.548 (chance 0.50), accuracy 0.629 (always predicting the training majority class: 0.600), sensitivity 0.952, specificity 0.143, F1 0.755 (TN 2, FP 12, FN 1, TP 20).

## Sensitivity analysis (original 107-participant preprocessing)
Selected C = 10, class_weight = None. Dataset 2 ROC-AUC = 0.481 (95% CI 0.271–0.684; n = 33: 14 controls, 19 psychosis). The interval includes 0.50, so above-chance discrimination is not supported. At threshold 0.50: balanced accuracy 0.547 (chance 0.50), accuracy 0.576 (always predicting the training majority class: 0.576), sensitivity 0.737, specificity 0.357, F1 0.667 (TN 5, FP 9, FN 5, TP 14).

The conclusion about chance-level discrimination is the same in both versions.
Training and test membership both differ between versions, so this is not an isolated test of channel omission. The 110-participant version remains primary.

## Original experiment, for the record
Original (fixed C = 1, no class weighting): ROC-AUC 0.476 (95% CI 0.262–0.684, 2,000 resamples). Archived unchanged; not replaced on the basis of test performance.

## Limitations
- The CI reflects test-sample uncertainty only, not training or model-selection uncertainty.
- Dataset 2 was seen before this revision; small test set (35, with 14 controls).
- Uneven exclusions (Dataset 1 8.5%, Dataset 2 42.6%); three recovered participants use 48 instead of 49 channels.
- No shared IDs, but person-level independence is unconfirmed; Dataset 1 includes ten acquisition-2 participants.
- The four relative powers sum to one; coefficients are not independent biological effects.
- Research analysis only, not a clinically validated diagnostic tool.
