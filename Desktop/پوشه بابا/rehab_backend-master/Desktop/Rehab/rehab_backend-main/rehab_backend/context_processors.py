def body_class_processor(request):
    """
    Adds appropriate body classes based on the current URL and view.
    """
    classes = []
    
    # Add app name as class
    if hasattr(request, 'resolver_match') and request.resolver_match:
        app_name = request.resolver_match.app_name
        url_name = request.resolver_match.url_name or ''
        
        # Add app name class
        if app_name:
            classes.append(f"app-{app_name.replace('_', '-')}")
        
        # Add URL name class
        if url_name:
            classes.append(f"page-{url_name.replace('_', '-')}")
        
        # Add specific page type classes
        if 'list' in url_name:
            classes.append('list-page')
        elif 'detail' in url_name:
            classes.append('detail-page')
        elif 'create' in url_name or 'add' in url_name:
            classes.append('form-page create-page')
        elif 'update' in url_name or 'edit' in url_name:
            classes.append('form-page update-page')
        elif 'delete' in url_name:
            classes.append('delete-page')
    
    # Add authentication status classes
    if hasattr(request, 'user') and request.user.is_authenticated:
        classes.append('user-authenticated')
        classes.append(f'user-{request.user.username}')
        if request.user.is_staff:
            classes.append('user-staff')
        if request.user.is_superuser:
            classes.append('user-superuser')
    else:
        classes.append('user-anonymous')
    
    # Add device type class (simplified)
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        classes.append('device-mobile')
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        classes.append('device-tablet')
    else:
        classes.append('device-desktop')
    
    # Add browser class (simplified)
    if 'chrome' in user_agent:
        classes.append('browser-chrome')
    elif 'firefox' in user_agent:
        classes.append('browser-firefox')
    elif 'safari' in user_agent and 'chrome' not in user_agent:
        classes.append('browser-safari')
    elif 'edge' in user_agent:
        classes.append('browser-edge')
    elif 'opera' in user_agent or 'opr/' in user_agent:
        classes.append('browser-opera')
    elif 'msie' in user_agent or 'trident/' in user_agent:
        classes.append('browser-ie')
    
    # Add OS class (simplified)
    if 'windows' in user_agent:
        classes.append('os-windows')
    elif 'mac os' in user_agent:
        classes.append('os-macos')
    elif 'linux' in user_agent and 'android' not in user_agent:
        classes.append('os-linux')
    elif 'android' in user_agent:
        classes.append('os-android')
    elif 'iphone' in user_agent or 'ipad' in user_agent or 'ipod' in user_agent:
        classes.append('os-ios')
    
    # Add time-based classes
    from datetime import datetime
    hour = datetime.now().hour
    if 5 <= hour < 12:
        classes.append('time-morning')
    elif 12 <= hour < 17:
        classes.append('time-noon')
    elif 17 <= hour < 20:
        classes.append('time-evening')
    else:
        classes.append('time-night')
    
    return {
        'body_class': ' '.join(classes).strip(),
    }
