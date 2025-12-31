import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PASTIS_ROOT = REPO_ROOT / "bin" / "third_party" / "pastis"
DISPERSION_ROOT = PASTIS_ROOT / "pastis" / "dispersion"
PASTISNB_ROOT = REPO_ROOT / "bin" / "third_party" / "pastisnb" / "scripts" / "dispersion"

if str(PASTIS_ROOT) not in sys.path:
    sys.path.insert(0, str(PASTIS_ROOT))
if str(DISPERSION_ROOT) not in sys.path:
    sys.path.insert(0, str(DISPERSION_ROOT))
if str(PASTISNB_ROOT) not in sys.path:
    sys.path.insert(0, str(PASTISNB_ROOT))