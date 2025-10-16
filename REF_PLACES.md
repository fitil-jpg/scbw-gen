# Місця для рефів у C коді

Цей документ показує всі місця, де можна додати рефи для покращення функціональності проекту.

## Основні файли

### src/main.c
- **REF_PLACE_1**: Глобальні змінні або константи
- **REF_PLACE_2**: Функція ініціалізації GLFW
- **REF_PLACE_3**: Функція створення вікна
- **REF_PLACE_4**: Функція ініціалізації GLAD
- **REF_PLACE_5**: Ініціалізація viewer
- **REF_PLACE_6**: Головний цикл рендерингу
- **REF_PLACE_7**: Функція очищення екрану
- **REF_PLACE_8**: Функція рендерингу
- **REF_PLACE_9**: Функція очищення ресурсів

### include/viewer.h
- **REF_PLACE_10**: Структури даних (Vector3, Matrix4, тощо)
- **REF_PLACE_11**: Константи (MAX_OBJECTS, WINDOW_WIDTH, тощо)
- **REF_PLACE_12**: Енуми (RenderMode, InputType, тощо)
- **REF_PLACE_13**: Поля структури Viewer
- **REF_PLACE_14**: Функції ініціалізації з конфігурацією
- **REF_PLACE_15**: Функції рендерингу (сцена, UI)
- **REF_PLACE_16**: Функції обробки подій (клавіатура, миша)
- **REF_PLACE_17**: Функції утиліт (кольори, шейдери)

### src/viewer.c
- **REF_PLACE_18**: Глобальні змінні
- **REF_PLACE_19**: Допоміжні функції
- **REF_PLACE_20**: Валідація параметрів
- **REF_PLACE_21**: Завантаження конфігурації
- **REF_PLACE_22**: Ініціалізація OpenGL об'єктів
- **REF_PLACE_23**: Створення шейдерів
- **REF_PLACE_24**: Створення буферів
- **REF_PLACE_25**: Підготовка до рендерингу
- **REF_PLACE_26**: Рендеринг сцени
- **REF_PLACE_27**: Рендеринг UI
- **REF_PLACE_28**: Пост-обробка
- **REF_PLACE_29**: Очищення OpenGL об'єктів
- **REF_PLACE_30**: Очищення шейдерів
- **REF_PLACE_31**: Очищення буферів
- **REF_PLACE_32**: Збереження стану

### src/viewer_utils.c
- **REF_PLACE_37**: Валідація параметрів
- **REF_PLACE_38**: Додаткові перевірки
- **REF_PLACE_39**: Завантаження конфігурації
- **REF_PLACE_40**: Парсинг JSON/XML
- **REF_PLACE_41**: Створення шейдерів
- **REF_PLACE_42**: Завантаження шейдерів з файлів
- **REF_PLACE_43**: Створення буферів
- **REF_PLACE_44**: Створення VBO/VAO
- **REF_PLACE_45**: Рендеринг сцени
- **REF_PLACE_46**: Рендеринг 3D об'єктів
- **REF_PLACE_47**: Рендеринг UI
- **REF_PLACE_48**: Рендеринг UI елементів
- **REF_PLACE_49**: Обробка клавіатури
- **REF_PLACE_50**: Обробка різних клавіш
- **REF_PLACE_51**: Обробка миші
- **REF_PLACE_52**: Обробка руху миші

### include/viewer_utils.h
- **REF_PLACE_53**: Додаткові структури
- **REF_PLACE_54**: Константи для утиліт
- **REF_PLACE_55**: Функції валідації
- **REF_PLACE_56**: Функції завантаження ресурсів
- **REF_PLACE_57**: Функції рендерингу
- **REF_PLACE_58**: Функції обробки подій
- **REF_PLACE_59**: Функції математики

### CMakeLists.txt
- **REF_PLACE_33**: Додаткові налаштування компілятора
- **REF_PLACE_34**: Додаткові цілі збірки
- **REF_PLACE_35**: MSVC налаштування
- **REF_PLACE_36**: GCC/Clang налаштування

## Приклади реалізації рефів

### Додавання математичних структур
```c
// REF_PLACE_10
typedef struct {
    float x, y, z;
} Vector3;

typedef struct {
    float m[16];
} Matrix4;
```

### Додавання констант
```c
// REF_PLACE_11
#define MAX_OBJECTS 1000
#define WINDOW_WIDTH 800
#define WINDOW_HEIGHT 600
```

### Додавання функцій рендерингу
```c
// REF_PLACE_15
void viewer_render_scene(Viewer* viewer);
void viewer_render_ui(Viewer* viewer);
void viewer_render_wireframe(Viewer* viewer);
```

### Додавання обробки подій
```c
// REF_PLACE_16
void viewer_handle_keyboard(Viewer* viewer, int key, int action);
void viewer_handle_mouse(Viewer* viewer, double x, double y);
void viewer_handle_resize(Viewer* viewer, int width, int height);
```

## Як використовувати

1. Знайдіть потрібний REF_PLACE_XX у коді
2. Замініть коментар на реальну реалізацію
3. Додайте відповідні заголовки у .h файли
4. Оновіть CMakeLists.txt якщо потрібно
5. Перевірте компіляцію та функціональність