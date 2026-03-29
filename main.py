from __future__ import annotations

from usecases.demo_organization import build_demo_organization_input
from usecases.us_iran_regional_crisis import build_us_iran_regional_crisis_input
from usecases.run_usecase import run_usecase


def main() -> None:
    run_usecase(build_us_iran_regional_crisis_input())
    # run_usecase(build_demo_organization_input())


if __name__ == "__main__":
    main()