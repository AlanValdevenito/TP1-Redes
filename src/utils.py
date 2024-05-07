from config import UPLOAD, DOWNLOAD


def check_verbose_quiet(args):
    if args.verbose and args.quiet:
        print('Error: Cannot use both verbose and quiet flags')
        return False
    return True


def check_client_args(args):
    if args.command == UPLOAD and not args.src:
        print('Error: Source file path is required for upload command')
        return False
    if args.command == DOWNLOAD and not args.dst:
        print('Error: Destination file path is required for download command')
        return False
    if not args.name:
        print('Error: File name is required')
        return False
    return check_verbose_quiet(args)


def check_server_args(args):
    return check_verbose_quiet(args)
