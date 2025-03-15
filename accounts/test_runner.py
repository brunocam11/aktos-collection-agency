import warnings
from django.test.runner import DiscoverRunner


class NoWarningsTestRunner(DiscoverRunner):
    """
    A test runner that silences specific warnings that we're aware of.
    """

    def setup_test_environment(self, **kwargs):
        # Filter out specific warnings we know about
        warnings.filterwarnings("ignore", message=".*should be a Decimal instance.*")
        warnings.filterwarnings("ignore", message=".*min_value.*")
        warnings.filterwarnings("ignore", message=".*max_value.*")

        # Continue with normal setup
        super().setup_test_environment(**kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # Run the tests with standard runner
        return super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)
