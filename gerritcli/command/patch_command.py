import gerritcli
import gerrit.utils.exceptions
import base64
import sys

class patch_command(gerritcli.maincommand):
    command = "patch"
    help = "patch command help"

    def init_argument(self):
        self.maincmd.add_argument('id', help='change number id')
        self.maincmd.add_argument('--revision', '-r', default='current', required=False)
        self.maincmd.add_argument('--path', required=False, nargs='+', action='append')
        gerritcli.utils.add_commmon_argument(self.maincmd, 'output')


    def handler(self, args):
        if args.output_file:
            f = open(args.output_file, 'w')
        else:
            f = sys.stdout

        client = gerritcli.gerrit_server.get_client()
        try:
            change = client.changes.get(args.id).to_dict()
        except gerrit.utils.exceptions.NotFoundError:
            print(f"change id {args.id} not found")
            return 1

        patch_url = f"/changes/{change['id']}/revisions/{args.revision}/patch"

        param = None
        if args.path:
            path = sum(args.path, [])
            print(path)
            param = {'path': path}

        try:
            patch = client.get(patch_url, params=param)
        except gerrit.utils.exceptions.NotFoundError as e:
            err_msg = f"change id {args.id}"
            if args.revision != "current":
                err_msg += f" or revision {args.revision}"
            if args.path:
                err_msg += f" or file {','.join(args.path)}"
            err_msg += f" not found, please check"
            print(err_msg, file=sys.stderr)
            return 1

        print(base64.b64decode(patch).decode(), file=f)
        if args.output_file:
            f.close()

        return 0


