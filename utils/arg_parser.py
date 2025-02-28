import argparse
from pathlib import Path

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    class ColoredHelpFormatter(argparse.HelpFormatter):
        def _format_action_invocation(self, action):
            if not action.option_strings:
                metavar, = self._metavar_formatter(action, action.dest)(1)
                return metavar
            else:
                parts = []
                if action.nargs == 0:
                    parts.extend(['\033[32m%s\033[0m' % opt for opt in action.option_strings])
                else:
                    default = action.dest.upper()
                    args_string = self._format_args(action, default)
                    for option_string in action.option_strings:
                        parts.append('\033[32m%s\033[0m %s' % (option_string, args_string))
                return ', '.join(parts)

        def _format_usage(self, usage, actions, groups, prefix):
            if prefix is None:
                prefix = '\033[36musage: \033[0m'
            return super()._format_usage(usage, actions, groups, prefix)

        def add_text(self, text):
            if text and text.startswith('optional arguments'):
                text = '\033[36moptional arguments:\033[0m'
            return super().add_text(text)

    parser = argparse.ArgumentParser(
        description="SiriusXM to USB - Download your favorite SiriusXM tracks to local storage",
        formatter_class=ColoredHelpFormatter
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "-d", "--destination",
        type=Path,
        default='.',
        help="Specify a destination folder"
    )
    parser.add_argument(
        "-l", "--log-file",
        type=Path,
        help="Log file path"
    )
    parser.add_argument(
        "-c", "--channel",
        type=str,
        default=None,
        action='append',
        required=True,
        help="Specify a channel to download.  You can specify multiple channels by using this flag multiple times."
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Will actually download the files"
    )
    return parser.parse_args()
