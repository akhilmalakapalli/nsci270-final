# Experiment 2 results summary

Question 2: how much does performance change from within Dataset 1 (nested cross-validation) to held-out Dataset 2?

- Internal ROC-AUC (nested CV, mean of 5 repeats × 5 folds): 0.615. Repeat AUCs ranged 0.581–0.659; single outer folds ranged 0.280–0.852 (split variability, not a CI).
- External ROC-AUC (Dataset 2, Experiment 1 model): 0.497 (95% bootstrap CI 0.289–0.704).
- Generalization gap (internal − external): +0.118, i.e. performance was lower on Dataset 2 than internally. Per-repeat gaps: +0.085, +0.134, +0.163, +0.084, +0.125.
- Balanced accuracy at 0.50: internal 0.555 vs external 0.548; sensitivity 0.778 vs 0.952; specificity 0.331 vs 0.143.
- Settings chosen in the 25 outer folds: C=0.1/None: 9, C=0.1/balanced: 3, C=1/None: 6, C=1/balanced: 2, C=10/None: 3, C=10/balanced: 2.
- For context only: Experiment 1's selection score (0.635) is optimistic and is not the internal estimate.

## Interpretation and limits
- Descriptive only: no significance test, because folds overlap and model selection adds uncertainty that the fold spread does not capture.
- The internal mean (0.615) lies inside the external 95% interval, so the size of the gap is very imprecise.
- Outer-fold models train on ~60 participants; the external model on all 75. This compares a procedure, not one fitted model.
- Sample composition, size, acquisition and exclusions (8.5% vs 42.6%) all differ between datasets; no single cause can be isolated.
- Dataset 2 was already examined, so this is exploratory. Person-level independence is unconfirmed; Dataset 1 includes ten acquisition-2 participants.
- Small samples (75 internal, 35 external), so all estimates are imprecise. Not a clinical tool.
