# /goal — Make the Z-ZOA holdout boundary machine-enforced

Implement a holdout security boundary for the Vela experiment.

## Required behavior

The selected MeerKAT validation catalogue(s) must be registered as `HOLDOUT` and must not be readable by training/reconstruction commands.

Create two execution contexts:

### AUDIT context
May read TRAIN and HOLDOUT only for leakage detection and exclusion-list creation. It must not:
- fit or tune reconstruction parameters;
- compute science performance metrics;
- create density/velocity reconstructions informed by holdout;
- expose holdout-derived tuning hints to the training config.

### TRAIN context
May read only approved `TRAIN_CLEAN` inputs. HOLDOUT directories should be unmounted, inaccessible, or denied at the data-loader layer.

### VALIDATE context
Allowed only after a frozen prediction manifest exists and passes hash verification.

## Tests

Write tests proving:
- TRAIN fails when asked for HOLDOUT;
- a hidden indirect parent dataset contaminated by HOLDOUT is also rejected;
- AUDIT can emit an exclusion list but not a reconstruction output;
- VALIDATE refuses to start without a valid freeze manifest;
- changing a training config after freeze invalidates validation authorization.

Make failure loud and explicit.
