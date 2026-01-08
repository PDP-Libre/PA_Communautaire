from pac_bdd.domain import *
from pytest_bdd import scenarios
import glob

# scenarios("../../docs/briques/04-validation-metier/compliance.feature")
# scenarios("compliance.feature")
# scenarios("format.feature")
# scenarios("pa_multiple.feature")
# scenarios("publish_article.feature")


# loop over all *.feature files
for feature_file in glob.glob("../../**/*.feature", recursive=True):
    # scenarios("../../docs/briques/04-validation-metier/compliance.feature")
    scenarios(feature_file)
