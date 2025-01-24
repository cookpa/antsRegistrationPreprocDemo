# antsRegistrationPreprocDemo

Python script that mirrors the "PreprocessImage" function in ANTs".

Some ANTs scripts have had histogram matching on by default, but this is rarely beneficial
and will be removed in futre releases.

If histogram matching is needed, it should be done as a preprocessing step. The ANTsPy
function `histogram_match2` has a better implementation and supports masks for the source
and reference domain specification.

This script is for demonstration purposes, so that the winsorization and preprocessing
steps can be visualized. As in ANTs, the winsorization is configurable by the user but the
histogram matching uses a a fixed set of parameters.

The script requires the ITK Python package, which is available from pip. It does not
require ANTs or ANTsPy.