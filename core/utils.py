from getpass import getpass


def console_menu(actions):
    """
    Menu para utilitarios de console
    :param actions:
    :return:
    """
    action_index = {}
    for a in actions:
        if a[0] in action_index:
            raise ValueError('Lista de ações inválida.')
        args = None
        if len(a) > 3:
            args = a[3]
        action_index[a[0]] = {
            'label': a[1],
            'function': a[2],
            'args': args,
        }

    while True:
        print('\n== Menu: ==')

        for i in actions:
            print(f'{i[0]}. {i[1]}')

        print('q. sair')
        res = get_prompt('Opção:')

        if res == 'q':
            print('Saindo...')
            break
        opt = int(res)
        a = action_index[opt]
        print(f'\n => {a["label"]}:')
        if a["args"]:
            a["function"](a["args"])
        else:
            a["function"]()


def wait_prompt(msg="Continue?"):
    response = get_prompt("%s [Y/n]" % msg, default="Y")
    return response in ('Y', 'y')


def get_prompt(name, default=None, hide_input=False, valid_options=None):
    while True:
        if hide_input:
            res = getpass("%s > " % name)
            if res:
                return res
        else:
            if default:
                res = input("%s [%s]> " % (name, default))
                if not res:
                    res = default
            elif valid_options:
                res = input("%s [%s]> " % (name, ', '.join(valid_options)))
                if not res:
                    continue
            else:
                res = input("%s > " % name)
                if not res:
                    continue

            if valid_options:
                if res in valid_options:
                    return res
                else:
                    print("Invalid option!")
            else:
                return res
