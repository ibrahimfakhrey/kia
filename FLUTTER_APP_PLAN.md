# KIA Flutter App - Comprehensive Development Plan

## Overview

This document outlines the complete development plan for the KIA (Kids International Academy) Flutter mobile application. The app serves as a parent portal allowing parents to view their children's information, access educational materials, and track payments.

---

## 1. Project Structure

```
kia_app/
├── lib/
│   ├── main.dart
│   ├── app.dart
│   │
│   ├── config/
│   │   ├── app_config.dart
│   │   ├── api_config.dart
│   │   ├── theme_config.dart
│   │   └── routes.dart
│   │
│   ├── core/
│   │   ├── constants/
│   │   │   ├── app_constants.dart
│   │   │   ├── api_endpoints.dart
│   │   │   └── storage_keys.dart
│   │   │
│   │   ├── errors/
│   │   │   ├── exceptions.dart
│   │   │   └── failures.dart
│   │   │
│   │   ├── network/
│   │   │   ├── api_client.dart
│   │   │   ├── api_interceptor.dart
│   │   │   └── network_info.dart
│   │   │
│   │   └── utils/
│   │       ├── validators.dart
│   │       ├── formatters.dart
│   │       └── helpers.dart
│   │
│   ├── data/
│   │   ├── models/
│   │   │   ├── user_model.dart
│   │   │   ├── student_model.dart
│   │   │   ├── subject_model.dart
│   │   │   ├── material_model.dart
│   │   │   └── payment_model.dart
│   │   │
│   │   ├── repositories/
│   │   │   ├── auth_repository.dart
│   │   │   ├── student_repository.dart
│   │   │   ├── subject_repository.dart
│   │   │   └── payment_repository.dart
│   │   │
│   │   └── datasources/
│   │       ├── remote/
│   │       │   ├── auth_remote_datasource.dart
│   │       │   ├── student_remote_datasource.dart
│   │       │   ├── subject_remote_datasource.dart
│   │       │   └── payment_remote_datasource.dart
│   │       │
│   │       └── local/
│   │           ├── auth_local_datasource.dart
│   │           └── cache_manager.dart
│   │
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── user.dart
│   │   │   ├── student.dart
│   │   │   ├── subject.dart
│   │   │   ├── material.dart
│   │   │   └── payment.dart
│   │   │
│   │   └── usecases/
│   │       ├── auth/
│   │       │   ├── login_usecase.dart
│   │       │   ├── logout_usecase.dart
│   │       │   └── refresh_token_usecase.dart
│   │       │
│   │       ├── student/
│   │       │   ├── get_students_usecase.dart
│   │       │   └── get_student_details_usecase.dart
│   │       │
│   │       ├── subject/
│   │       │   ├── get_subjects_usecase.dart
│   │       │   └── get_materials_usecase.dart
│   │       │
│   │       └── payment/
│   │           ├── get_payments_usecase.dart
│   │           └── get_payment_summary_usecase.dart
│   │
│   ├── presentation/
│   │   ├── blocs/
│   │   │   ├── auth/
│   │   │   │   ├── auth_bloc.dart
│   │   │   │   ├── auth_event.dart
│   │   │   │   └── auth_state.dart
│   │   │   │
│   │   │   ├── student/
│   │   │   │   ├── student_bloc.dart
│   │   │   │   ├── student_event.dart
│   │   │   │   └── student_state.dart
│   │   │   │
│   │   │   ├── subject/
│   │   │   │   ├── subject_bloc.dart
│   │   │   │   ├── subject_event.dart
│   │   │   │   └── subject_state.dart
│   │   │   │
│   │   │   └── payment/
│   │   │       ├── payment_bloc.dart
│   │   │       ├── payment_event.dart
│   │   │       └── payment_state.dart
│   │   │
│   │   ├── screens/
│   │   │   ├── splash/
│   │   │   │   └── splash_screen.dart
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── login_screen.dart
│   │   │   │   └── forgot_password_screen.dart
│   │   │   │
│   │   │   ├── home/
│   │   │   │   └── home_screen.dart
│   │   │   │
│   │   │   ├── students/
│   │   │   │   ├── students_list_screen.dart
│   │   │   │   └── student_details_screen.dart
│   │   │   │
│   │   │   ├── subjects/
│   │   │   │   ├── subjects_list_screen.dart
│   │   │   │   └── subject_details_screen.dart
│   │   │   │
│   │   │   ├── materials/
│   │   │   │   ├── materials_list_screen.dart
│   │   │   │   ├── pdf_viewer_screen.dart
│   │   │   │   └── video_player_screen.dart
│   │   │   │
│   │   │   ├── payments/
│   │   │   │   ├── payments_screen.dart
│   │   │   │   └── payment_details_screen.dart
│   │   │   │
│   │   │   └── profile/
│   │   │       └── profile_screen.dart
│   │   │
│   │   └── widgets/
│   │       ├── common/
│   │       │   ├── app_bar_widget.dart
│   │       │   ├── loading_widget.dart
│   │       │   ├── error_widget.dart
│   │       │   ├── empty_state_widget.dart
│   │       │   └── custom_button.dart
│   │       │
│   │       ├── cards/
│   │       │   ├── student_card.dart
│   │       │   ├── subject_card.dart
│   │       │   ├── material_card.dart
│   │       │   └── payment_card.dart
│   │       │
│   │       └── dialogs/
│   │           ├── confirmation_dialog.dart
│   │           └── error_dialog.dart
│   │
│   └── injection_container.dart
│
├── assets/
│   ├── images/
│   │   ├── logo.png
│   │   ├── placeholder_avatar.png
│   │   └── empty_state.png
│   │
│   ├── icons/
│   │   └── app_icons.ttf
│   │
│   └── fonts/
│       ├── Cairo-Regular.ttf
│       ├── Cairo-Bold.ttf
│       └── Cairo-SemiBold.ttf
│
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
│
└── pubspec.yaml
```

---

## 2. Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter

  # State Management
  flutter_bloc: ^8.1.3
  equatable: ^2.0.5

  # Networking
  dio: ^5.4.0

  # Local Storage
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.2

  # Dependency Injection
  get_it: ^7.6.4
  injectable: ^2.3.2

  # Navigation
  go_router: ^13.0.0

  # UI Components
  flutter_svg: ^2.0.9
  cached_network_image: ^3.3.1
  shimmer: ^3.0.0

  # Media
  flutter_pdfview: ^1.3.2
  youtube_player_flutter: ^9.0.1
  url_launcher: ^6.2.2

  # Utils
  intl: ^0.19.0
  connectivity_plus: ^5.0.2

  # Arabic Support
  flutter_localizations:
    sdk: flutter

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  build_runner: ^2.4.7
  injectable_generator: ^2.4.1
  bloc_test: ^9.1.5
  mocktail: ^1.0.1
```

---

## 3. API Endpoints

Based on the backend analysis, the following endpoints are available:

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Parent login |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/auth/me` | Get current user profile |

### Students
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/students` | Get all children of parent |
| GET | `/api/students/{id}` | Get single student details |
| GET | `/api/students/{id}/subjects` | Get subjects for student's class |
| GET | `/api/students/{id}/payments` | Get payments for student |

### Subjects & Materials
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subjects/{id}` | Get subject details |
| GET | `/api/subjects/{id}/materials` | Get materials for subject |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments/summary` | Get payment summary for all children |

---

## 4. Data Models

### User Model
```dart
class UserModel {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String role;
  final bool isActive;
  final DateTime createdAt;
}
```

### Student Model
```dart
class StudentModel {
  final int id;
  final int parentId;
  final int? classId;
  final String? className;
  final String fullName;
  final DateTime? dateOfBirth;
  final String? profileImageUrl;
  final DateTime createdAt;
}
```

### Subject Model
```dart
class SubjectModel {
  final int id;
  final int classId;
  final String? className;
  final String name;
  final String? description;
  final int materialCount;
  final DateTime createdAt;
}
```

### Material Model
```dart
class MaterialModel {
  final int id;
  final int subjectId;
  final String? subjectName;
  final String title;
  final String type; // 'file' or 'video'
  final String? fileUrl;
  final String? videoUrl;
  final int orderIndex;
  final DateTime createdAt;
}
```

### Payment Model
```dart
class PaymentModel {
  final int id;
  final int studentId;
  final String? studentName;
  final double amount;
  final DateTime dueDate;
  final DateTime? paidDate;
  final bool isPaid;
  final String? notes;
  final DateTime createdAt;
}
```

---

## 5. Screens & Features

### 5.1 Splash Screen
- App logo animation
- Check authentication status
- Navigate to login or home

### 5.2 Login Screen
- Email input field
- Password input field with visibility toggle
- Login button with loading state
- Error handling and display
- Arabic RTL support

### 5.3 Home Screen (Dashboard)
- Welcome message with parent name
- Children overview cards (quick access)
- Payment summary widget
- Quick actions (view materials, payments)
- Bottom navigation bar

### 5.4 Students Screen
- List of all children
- Student cards showing:
  - Profile image (or placeholder)
  - Name
  - Class name
  - Age (calculated from DOB)
- Tap to view student details

### 5.5 Student Details Screen
- Student profile header
- Class information
- Subjects grid/list
- Recent payments
- Quick action buttons

### 5.6 Subjects Screen
- List of subjects for selected student
- Subject cards showing:
  - Subject name
  - Description
  - Material count
- Tap to view materials

### 5.7 Materials Screen
- List of materials for selected subject
- Material cards showing:
  - Title
  - Type (PDF/Video icon)
  - Tap to open viewer

### 5.8 PDF Viewer Screen
- Full-screen PDF viewer
- Page navigation
- Zoom controls
- Share/Download option

### 5.9 Video Player Screen
- YouTube embedded player
- Fullscreen support
- Playback controls

### 5.10 Payments Screen
- Overall payment summary card
- Per-child payment breakdown
- Payment history list
- Status indicators (paid/pending/overdue)
- Filter by status

### 5.11 Profile Screen
- User information display
- Language toggle (Arabic/English)
- Logout button
- App version info

---

## 6. State Management (BLoC Pattern)

### Auth BLoC
```dart
// Events
abstract class AuthEvent {}
class LoginRequested extends AuthEvent { ... }
class LogoutRequested extends AuthEvent { ... }
class CheckAuthStatus extends AuthEvent { ... }
class RefreshTokenRequested extends AuthEvent { ... }

// States
abstract class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class Authenticated extends AuthState { final User user; }
class Unauthenticated extends AuthState {}
class AuthError extends AuthState { final String message; }
```

### Student BLoC
```dart
// Events
abstract class StudentEvent {}
class LoadStudents extends StudentEvent { ... }
class LoadStudentDetails extends StudentEvent { final int studentId; }

// States
abstract class StudentState {}
class StudentInitial extends StudentState {}
class StudentLoading extends StudentState {}
class StudentsLoaded extends StudentState { final List<Student> students; }
class StudentDetailsLoaded extends StudentState { final Student student; }
class StudentError extends StudentState { final String message; }
```

### Subject BLoC
```dart
// Events
abstract class SubjectEvent {}
class LoadSubjects extends SubjectEvent { final int studentId; }
class LoadMaterials extends SubjectEvent { final int subjectId; }

// States
abstract class SubjectState {}
class SubjectInitial extends SubjectState {}
class SubjectLoading extends SubjectState {}
class SubjectsLoaded extends SubjectState { final List<Subject> subjects; }
class MaterialsLoaded extends SubjectState { final List<Material> materials; }
class SubjectError extends SubjectState { final String message; }
```

### Payment BLoC
```dart
// Events
abstract class PaymentEvent {}
class LoadPaymentSummary extends PaymentEvent { ... }
class LoadStudentPayments extends PaymentEvent { final int studentId; }

// States
abstract class PaymentState {}
class PaymentInitial extends PaymentState {}
class PaymentLoading extends PaymentState {}
class PaymentSummaryLoaded extends PaymentState { final PaymentSummary summary; }
class PaymentsLoaded extends PaymentState { final List<Payment> payments; }
class PaymentError extends PaymentState { final String message; }
```

---

## 7. Theme & Styling

### Colors
```dart
class AppColors {
  // Primary Colors
  static const primary = Color(0xFF667EEA);
  static const primaryDark = Color(0xFF764BA2);

  // Status Colors
  static const success = Color(0xFF28A745);
  static const warning = Color(0xFFFFC107);
  static const error = Color(0xFFDC3545);
  static const info = Color(0xFF17A2B8);

  // Neutral Colors
  static const background = Color(0xFFF8F9FA);
  static const surface = Color(0xFFFFFFFF);
  static const textPrimary = Color(0xFF212529);
  static const textSecondary = Color(0xFF6C757D);
  static const border = Color(0xFFDEE2E6);
}
```

### Typography
```dart
class AppTypography {
  static const fontFamily = 'Cairo';

  static const headline1 = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.bold,
    fontFamily: fontFamily,
  );

  static const headline2 = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w600,
    fontFamily: fontFamily,
  );

  static const bodyLarge = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    fontFamily: fontFamily,
  );

  static const bodyMedium = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    fontFamily: fontFamily,
  );

  static const caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    fontFamily: fontFamily,
  );
}
```

---

## 8. Localization (Arabic Support)

### Setup
- Configure RTL support
- Use `flutter_localizations`
- Store language preference

### Strings (Arabic)
```dart
// lib/l10n/app_ar.arb
{
  "appTitle": "أكاديمية كيا الدولية",
  "login": "تسجيل الدخول",
  "email": "البريد الإلكتروني",
  "password": "كلمة المرور",
  "logout": "تسجيل الخروج",
  "home": "الرئيسية",
  "students": "الطلاب",
  "subjects": "المواد",
  "materials": "المحتوى التعليمي",
  "payments": "المدفوعات",
  "profile": "الملف الشخصي",
  "welcome": "مرحباً",
  "myChildren": "أطفالي",
  "viewAll": "عرض الكل",
  "noData": "لا توجد بيانات",
  "loading": "جاري التحميل...",
  "error": "حدث خطأ",
  "retry": "إعادة المحاولة",
  "paid": "مدفوع",
  "pending": "معلق",
  "overdue": "متأخر",
  "totalDue": "إجمالي المستحق",
  "dueDate": "تاريخ الاستحقاق",
  "class": "الفصل",
  "age": "العمر",
  "years": "سنوات"
}
```

---

## 9. Navigation (go_router)

```dart
final router = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(
      path: '/splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
    ShellRoute(
      builder: (context, state, child) => MainShell(child: child),
      routes: [
        GoRoute(
          path: '/home',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/students',
          builder: (context, state) => const StudentsListScreen(),
          routes: [
            GoRoute(
              path: ':id',
              builder: (context, state) => StudentDetailsScreen(
                studentId: int.parse(state.pathParameters['id']!),
              ),
            ),
          ],
        ),
        GoRoute(
          path: '/subjects/:studentId',
          builder: (context, state) => SubjectsListScreen(
            studentId: int.parse(state.pathParameters['studentId']!),
          ),
          routes: [
            GoRoute(
              path: ':subjectId/materials',
              builder: (context, state) => MaterialsListScreen(
                subjectId: int.parse(state.pathParameters['subjectId']!),
              ),
            ),
          ],
        ),
        GoRoute(
          path: '/payments',
          builder: (context, state) => const PaymentsScreen(),
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
    ),
    GoRoute(
      path: '/pdf-viewer',
      builder: (context, state) => PdfViewerScreen(
        url: state.extra as String,
      ),
    ),
    GoRoute(
      path: '/video-player',
      builder: (context, state) => VideoPlayerScreen(
        videoUrl: state.extra as String,
      ),
    ),
  ],
);
```

---

## 10. API Client Implementation

```dart
class ApiClient {
  late final Dio _dio;
  final FlutterSecureStorage _storage;

  ApiClient(this._storage) {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConfig.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _dio.interceptors.add(AuthInterceptor(_storage, _dio));
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }

  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }
}

class AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;
  final Dio _dio;

  AuthInterceptor(this._storage, this._dio);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.read(key: StorageKeys.accessToken);
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Try to refresh token
      final refreshToken = await _storage.read(key: StorageKeys.refreshToken);
      if (refreshToken != null) {
        try {
          final response = await _dio.post(
            '/api/auth/refresh',
            options: Options(headers: {'Authorization': 'Bearer $refreshToken'}),
          );

          final newToken = response.data['access_token'];
          await _storage.write(key: StorageKeys.accessToken, value: newToken);

          // Retry original request
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          final retryResponse = await _dio.fetch(err.requestOptions);
          return handler.resolve(retryResponse);
        } catch (e) {
          // Refresh failed, logout user
          await _storage.deleteAll();
        }
      }
    }
    handler.next(err);
  }
}
```

---

## 11. Security Considerations

1. **Token Storage**: Use `flutter_secure_storage` for storing JWT tokens
2. **Certificate Pinning**: Implement SSL pinning for production
3. **Input Validation**: Validate all user inputs
4. **Sensitive Data**: Never log sensitive information
5. **Session Management**: Auto-logout on token expiry
6. **API Security**: All endpoints require authentication

---

## 12. Testing Strategy

### Unit Tests
- Repository tests
- Use case tests
- BLoC tests
- Model serialization tests

### Widget Tests
- Screen rendering tests
- User interaction tests
- Form validation tests

### Integration Tests
- Full flow tests
- API integration tests

---

## 13. Development Phases

### Phase 1: Foundation
- Project setup
- Dependencies configuration
- Theme and styling
- Navigation setup
- API client setup
- Dependency injection

### Phase 2: Authentication
- Login screen UI
- Auth BLoC implementation
- Token management
- Auto-login functionality

### Phase 3: Core Features
- Home screen dashboard
- Students list and details
- Profile screen

### Phase 4: Educational Content
- Subjects list screen
- Materials list screen
- PDF viewer integration
- Video player integration

### Phase 5: Payments
- Payment summary screen
- Payment details
- Status indicators

### Phase 6: Polish
- Arabic localization
- Error handling improvements
- Loading states
- Empty states
- Pull-to-refresh
- Offline support (caching)

### Phase 7: Testing & QA
- Unit tests
- Widget tests
- Integration tests
- Bug fixes

### Phase 8: Deployment
- App icons and splash
- Play Store listing
- App Store listing
- Release builds

---

## 14. File-by-File Implementation Order

1. `pubspec.yaml` - Dependencies
2. `lib/main.dart` - App entry point
3. `lib/config/` - Configuration files
4. `lib/core/` - Core utilities and network
5. `lib/data/models/` - Data models
6. `lib/domain/entities/` - Domain entities
7. `lib/data/datasources/` - API data sources
8. `lib/data/repositories/` - Repositories
9. `lib/domain/usecases/` - Use cases
10. `lib/presentation/blocs/auth/` - Auth state management
11. `lib/presentation/screens/splash/` - Splash screen
12. `lib/presentation/screens/auth/` - Login screen
13. `lib/presentation/blocs/student/` - Student state management
14. `lib/presentation/screens/home/` - Home screen
15. `lib/presentation/screens/students/` - Student screens
16. `lib/presentation/blocs/subject/` - Subject state management
17. `lib/presentation/screens/subjects/` - Subject screens
18. `lib/presentation/screens/materials/` - Material screens
19. `lib/presentation/blocs/payment/` - Payment state management
20. `lib/presentation/screens/payments/` - Payment screens
21. `lib/presentation/screens/profile/` - Profile screen
22. `lib/injection_container.dart` - DI setup
23. Localization files
24. Tests

---

## 15. Backend API Response Examples

### Login Response
```json
{
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG...",
  "user": {
    "id": 2,
    "email": "ahmed@test.com",
    "full_name": "Ahmed Al-Rashid",
    "phone": "0501234567",
    "role": "parent",
    "is_active": true,
    "created_at": "2026-01-26T15:48:49.875126"
  }
}
```

### Students Response
```json
[
  {
    "id": 1,
    "parent_id": 2,
    "class_id": 3,
    "class_name": "KG1",
    "full_name": "Yusuf Ahmed",
    "date_of_birth": "2019-03-15",
    "profile_image_url": null,
    "created_at": "2026-01-26T15:48:50.692454"
  }
]
```

### Subjects Response
```json
[
  {
    "id": 1,
    "class_id": 3,
    "class_name": "KG1",
    "name": "Math",
    "description": "Numbers and counting",
    "material_count": 0,
    "created_at": "2026-01-26T15:30:59.490557"
  }
]
```

### Materials Response
```json
[
  {
    "id": 3,
    "subject_id": 2,
    "subject_name": "English",
    "title": "English ABC",
    "type": "file",
    "file_url": null,
    "video_url": null,
    "order_index": 0,
    "created_at": "2026-01-26T15:48:50.700330"
  }
]
```

### Payment Summary Response
```json
{
  "total_due": 10500.0,
  "total_paid": 0,
  "pending_count": 2,
  "children_summary": [
    {
      "student": { ... },
      "total_due": 5000.0,
      "total_paid": 0,
      "next_payment": { ... }
    }
  ]
}
```

---

## 16. Notes

- The backend is already running and tested at `http://127.0.0.1:5000`
- All API endpoints require JWT authentication except `/api/auth/login`
- The app should support both Arabic (RTL) and English (LTR)
- Default language should be Arabic
- Cairo font is recommended for Arabic text
- Material Design 3 guidelines should be followed

---

## 17. Contact

For backend API questions or issues, refer to the Flask backend code in the `/kia` directory.
