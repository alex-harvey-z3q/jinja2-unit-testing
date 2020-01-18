#!/usr/bin/env python3

import unittest
import jinja2
import os, yaml, subprocess

COMPILED = '.compiled-j2'
DEVNULL = open(os.devnull, 'w')


class TestJ2(unittest.TestCase):

    with open('pyunit/fixtures/test_j2.yml', 'r') as stream:
        try:
            test_data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    def setUp(self):
        if not os.path.exists(COMPILED):
            os.makedirs(COMPILED)

    def test_j2(self):
        """
        Using test data sets found in pyunit/fixtures/test_j2.yml,
        ensure that all Jinja2 templates compile and that the generated
        CloudFormation templates validate.
        """

        for full_path, contexts in self.test_data.items():

            for count, context in enumerate(contexts):

                path = os.path.dirname(full_path)
                file_name = os.path.basename(full_path)

                compiled = '{}/{}.{}'.format(
                        COMPILED, file_name.replace('.j2',''), count)

                rendered = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(path)
                ).get_template(file_name).render(context)

                with open(compiled, 'w') as text_file:
                    text_file.write(rendered)

                try:
                    yaml.load(rendered, Loader=yaml.BaseLoader)
                except:
                    self.fail("Compiled template is not valid YAML")

                try:
                    print("Validating {} ...".format(compiled))
                    command = "aws cloudformation validate-template \
                            --template-body file://{}".format(compiled)
                    subprocess.check_call(command.split(), stdout=DEVNULL)
                except:
                    self.fail("Validate template failed")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
