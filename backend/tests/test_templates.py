from app.formations.templates import generate_template
from app.models.domain import TemplateKind, TemplateRequest


def test_line_template_is_deterministic_and_centered() -> None:
    slots = generate_template(TemplateRequest(kind=TemplateKind.LINE, count=3, column_spacing=2))
    assert [slot.position.x for slot in slots] == [-2, 0, 2]
    assert [slot.id for slot in slots] == ["slot-1", "slot-2", "slot-3"]

