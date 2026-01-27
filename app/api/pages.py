from flask import jsonify
from . import api_bp


@api_bp.route('/pages/privacy-policy', methods=['GET'])
def privacy_policy():
    """Get privacy policy content."""
    content = {
        'title': 'Privacy Policy',
        'last_updated': '2026-01-27',
        'sections': [
            {
                'heading': 'Introduction',
                'content': 'Welcome to KIA. We respect your privacy and are committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information when you use our application.'
            },
            {
                'heading': 'Information We Collect',
                'content': 'We collect information you provide directly to us, including: name, email address, phone number, student information, and payment details. We also automatically collect certain information about your device and usage of our services.'
            },
            {
                'heading': 'How We Use Your Information',
                'content': 'We use the information we collect to: provide and maintain our services, process transactions, send notifications about your account, respond to your requests, and improve our services.'
            },
            {
                'heading': 'Data Security',
                'content': 'We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the Internet is 100% secure.'
            },
            {
                'heading': 'Data Sharing',
                'content': 'We do not sell, trade, or rent your personal information to third parties. We may share your information only with service providers who assist us in operating our application and conducting our business.'
            },
            {
                'heading': 'Your Rights',
                'content': 'You have the right to access, correct, or delete your personal information. You may also request a copy of your data or ask us to restrict processing of your information.'
            },
            {
                'heading': 'Children\'s Privacy',
                'content': 'Our service involves managing student information. We take extra care to protect children\'s data and only collect information necessary for educational purposes with parental consent.'
            },
            {
                'heading': 'Changes to This Policy',
                'content': 'We may update this privacy policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "last updated" date.'
            },
            {
                'heading': 'Contact Us',
                'content': 'If you have any questions about this privacy policy, please contact us at support@kia-app.com.'
            }
        ]
    }

    return jsonify(content), 200
