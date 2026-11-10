<!-- SPDX-License-Identifier: Apache-2.0 -->

# Prep-tool technical debt

Status: seven previously reported failures, separate from institutional answer
scoring. This record does not skip tests, mark failures expected, change fixtures,
or claim the root suite is green. The 2026-11-09 log records 450 passed and these
seven failures. The test cache also has historical entries outside this list;
it is not a fresh full-suite result. No full-suite rerun is claimed here.

- `tests/test_cli.py::test_prepare_command_exits_zero`
- `tests/test_prompt_builder.py::test_table_like_chunk_gets_bounded_records_instruction`
- `tests/test_prompt_builder.py::test_prose_chunk_still_gets_a_bounded_records_instruction`
- `tests/test_runner_mock.py::test_runner_validation_passes`
- `tests/test_runner_mock.py::test_prose_source_produces_generic_records`
- `tests/test_runner_mock.py::test_table_like_source_produces_ingredient_reference_records`
- `tests/test_runner_mock.py::test_progress_callback_exception_does_not_break_run`

These failures concern `okpf-prep` preparation, bounded prompts, mock records and
callbacks. They are neither model-answer observations nor scores for the ordering
study. The study uses a retained reference CLI export, frozen inputs and its own
runner; preparation tests are not mixed into its denominators or evaluator packet.
This separation is a scope statement, not proof of absence of all harness defects.
Any subsequently discovered evaluation defect must be recorded on its own merits.

Next step in a separately scoped fix: reproduce the seven exact tests, diagnose
their failures, make focused fixes and run relevant regressions. Preserve the
frozen experiment rather than rebuilding it from newly changed preparation code.
