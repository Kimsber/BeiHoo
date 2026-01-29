from django import template

register = template.Library()

@register.inclusion_tag('components/role_badge.html')
def role_badge(role):
    """
    Display a colored badge for user role
    Usage: {% role_badge user.role %}
    """
    role_config = {
        'admin': {'label': '系統管理員', 'color': 'bg-danger'},
        'doctor': {'label': '醫師', 'color': 'bg-primary'},
        'therapist': {'label': '治療師', 'color': 'bg-info'},
        'nurse': {'label': '護理師', 'color': 'bg-success'},
        'case_manager': {'label': '個管師', 'color': 'purple', 'custom': True},
        'caregiver': {'label': '照服員', 'color': 'teal', 'custom': True},
        'patient': {'label': '病患', 'color': 'bg-secondary'},
        'researcher': {'label': '研究員', 'color': 'bg-warning'},
    }
    
    config = role_config.get(role, {'label': role, 'color': 'bg-secondary'})
    
    return {
        'label': config['label'],
        'color': config['color'],
        'is_custom': config.get('custom', False)
    }