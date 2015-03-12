import sublime
import sublime_plugin
import re
import subprocess
import math

# Tests 1 10 101 123 999 0x1c


class JaMathDecHexCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sel = self.view.sel()

        # replace all regions with math alteration
        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            if text.isdecimal():
                self.view.replace(edit, region, "0x%x" % int(text))


class JaMathHexDecCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sel = self.view.sel()

        # replace all regions with math alteration
        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            if re.findall('^0x[a-f0-9]+$', text):
                self.view.replace(edit, region, str(int(text, 16)))


class JaPhpUnserializeCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sel = self.view.sel()

        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            cleanText = text.replace("'", "\\'")
            unserialized = subprocess.Popen(["php",
                                             "-r",
                                             "ini_set('display_errors', 1); var_export(unserialize('" + cleanText + "'));"],
                                            stdout=subprocess.PIPE).communicate()[0]

            if unserialized != "false" or text == 'b:0;':
                self.view.replace(edit, region, unserialized.decode("utf-8"))
            else:
                pass


class JaPhpSerializeCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sel = self.view.sel()

        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            serialized = subprocess.Popen(["php",
                                           "-r",
                                           "ini_set('display_errors', 1); echo serialize(" + text + ");"],
                                          stdout=subprocess.PIPE).communicate()[0]

            self.view.replace(edit, region, serialized.decode("utf-8"))


class JaColumnizerCommand(sublime_plugin.TextCommand):

    def run(self, edit, columns):
        sel = self.view.sel()

        if columns == "fit":
            width = int(self.view.settings().get("rulers")[0])
        else:
            width = 0

        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            # 3. Fit them 2 or 3 cols, needs to be configurable

            lines = text.split("\n")
            lines = [s.strip() for s in lines]

            # Find the longest line, add 1 to it for padding
            longest = 0
            for line in lines:
                length = len(line) + 1
                longest = max(longest, length)

            # Try an calculate the fit of the longest line into the
            if columns == "fit":
                columns = math.floor(width / longest)

            columns = int(columns)

            # Never try to columnize for a non-positive number of columns!
            if columns > 0:
                # The printf format string for each column, eg: "%-30s"
                fmt = "%-" + str(longest) + "s"
                rows = []

                while True: # Sorta do-while loop
                    row = []
                    for i in range(columns):
                        row.append(self.unshiftLine(lines))

                    rows.append(((fmt * columns) % tuple(row)).rstrip())

                    if len(lines) <= 0:
                        break

                self.view.replace(edit, region, "\n".join(rows))

    def unshiftLine(self, lines):
        if len(lines) <= 0:
            return ''
        else:
            return lines.pop(0)


# command: ja_reindent
class JaReindentCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        sel = self.view.sel()

        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            self.view.replace(edit, region, self.reindent(text))

    def reindent(self, text):
        result = ''

        openers = ['[', '(']
        closers = [']', ')']
        endels = [',']
        tab = '    '
        depth = 0

        for char in text:
            if char in openers:
                result += '\n' + (tab * depth) + char
                depth += 1
                result += '\n' + (tab * depth)
            elif char in closers:
                depth -= 1
                result += '\n' + (tab * depth) + char
            elif char in endels:
                result += char + '\n' + (tab * depth)
            else:
                result += char

            if depth < 0:
                result = "Parse error"
                break

        return result


# command: ja_toseconds
class JaToSecondsCommand(sublime_plugin.TextCommand):
    multipliers = [86400, 3600, 60, 1]

    regex = re.compile(r"""
        (?:([\-\+]?\d+)[ ]day[s]?[ ]?)?
        (?:([\-\+]?\d+)[ ]hr[s]?[ ]?)?
        (?:([\-\+]?\d+)[ ]min[s]?[ ]?)?
        (?:([\-\+]?\d+)[ ]sec[o]?[n]?[d]?[s]?)?
    """, re.VERBOSE)

    def run(self, edit):
        sel = self.view.sel()

        for region in sel:
            word = self.view.word(region)
            text = self.view.substr(word)

            self.view.replace(edit, region, self.to_seconds(text))

    def to_seconds(self, text):
        result = 0

        m = self.regex.findall(text)

        for i, mult in enumerate(self.multipliers):
            result += int(m[0][i] if m[0][i] else '0') * mult

        return str(result)
