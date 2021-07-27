from tempest.lib.cli import output_parser

def parse_details(output):
    """ Takes a two-column table with "Field" and "Value" headers from the
            output of an OpenStack CLI command (e.g. "user create",
            "project show") as an argument.
        Returns a dict with entries corresponding to the table's rows. """
    details = {}
    for item in output_parser.listing(output):
        details.update({ item['Field']: item['Value'] })
    return details

def kwargs_to_flags(valid_flags, arguments):
    """ Takes an iterable containing a list of valid flags and a flattened
            kwargs dict containing the flag values received by the function.
        The key for each dict entry should be the name of a valid flag for the
            command being run, with any hypnens in the flag name replaced with
            underscores (e.g. end-time -> end_time). Its corresponding value
            should be a string, True (if that flag is included by itself),
            or None/False to indicate the flag should be excluded.
        Returns a stringified version of kwargs for use with CLI commands. """
    flag_string = ''
    for flag in arguments.keys():
        val = arguments[flag]
        if val is not None:
            if flag in valid_flags:
                tmp = ' --%s' % flag.replace('_', '-')
                if type(val) == str:
                    flag_string += '%s "%s"' % (tmp, val)
                elif type(val) == bool:
                    flag_string += tmp if val else ''
                else:
                    raise TypeError('Invalid value for flag %s, expected value \
                            of type \'str\' or \'bool\' and got type \'%s\'' %
                            (flag, type(val).__name__))
            else:
                raise NameError('Invalid flag with name %s' % flag)
    return flag_string
