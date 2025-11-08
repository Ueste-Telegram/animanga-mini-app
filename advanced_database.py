import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class AdvancedDatabase:
    def __init__(self):
        self.data_file = "animanga_advanced_data.json"
        self.load_data()
    
    def load_data(self):
        """Загружаем данные из файла или создаем новую структуру"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print("✅ База данных загружена")
            except Exception as e:
                print(f"❌ Ошибка загрузки базы: {e}")
                self.create_new_database()
        else:
            self.create_new_database()
    
    def create_new_database(self):
        """Создаем новую структуру базы данных"""
        self.data = {
            "users": {},
            "anime_cache": {},      # Кэш данных аниме из внешних API
            "manga_cache": {},      # Кэш данных манги из внешних API
            "genres": {             # Справочник жанров
                "anime": ["Сёнэн", "Сёдзё", "Фэнтези", "Романтика", "Комедия", "Драма", "Экшен", "Приключения", "Повседневность", "Гарем", "Меха", "Мистика", "Ужасы", "Сёнэн-ай", "Сёдзё-ай", "Спокон", "Детектив", "Психологическое", "Исторический", "Научная фантастика", "Киберпанк", "Постапокалипсис", "Исекай", "Махо-сёдзё", "Сэйнэн", "Дзёсэй"],
                "manga": ["Сёнэн", "Сёдзё", "Сэйнэн", "Дзёсэй", "Фэнтези", "Романтика", "Комедия", "Драма", "Экшен", "Приключения", "Повседневность", "Гарем", "Меха", "Мистика", "Ужасы", "Сёнэн-ай", "Сёдзё-ай", "Спокон", "Детектив", "Психологическое", "Исторический", "Научная фантастика", "Киберпанк", "Постапокалипсис", "Исекай", "Махо-сёдзё", "Боевик", "Гурман"]
            },
            "statuses": {           # Статусы просмотра/чтения
                "anime": {
                    "watching": "👀 Смотрю",
                    "completed": "✅ Просмотрено", 
                    "planned": "📋 В планах",
                    "dropped": "❌ Брошено",
                    "rewatching": "🔁 Пересматриваю",
                    "on_hold": "⏸️ На паузе"
                },
                "manga": {
                    "reading": "📖 Читаю",
                    "completed": "✅ Прочитано",
                    "planned": "📋 В планах",
                    "dropped": "❌ Брошено",
                    "rereading": "🔁 Перечитываю",
                    "on_hold": "⏸️ На паузе"
                }
            }
        }
        self.save_data()
        print("✅ Создана новая база данных")
    
    def save_data(self):
        """Сохраняем данные в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def get_user_data(self, user_id: int) -> Dict:
        """Получаем или создаем данные пользователя"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {
                "profile": {
                    "username": "",
                    "join_date": datetime.now().isoformat(),
                    "bio": "",
                    "favorite_genres": [],
                    "preferences": {
                        "default_anime_status": "planned",
                        "default_manga_status": "planned",
                        "time_format": "minutes",  # minutes, hours, days
                        "private_profile": False
                    }
                },
                "stats": {
                    "anime": {
                        "total_count": 0,
                        "watching_count": 0,
                        "completed_count": 0,
                        "planned_count": 0,
                        "dropped_count": 0,
                        "total_watch_time": 0,  # в минутах
                        "mean_score": 0
                    },
                    "manga": {
                        "total_count": 0,
                        "reading_count": 0,
                        "completed_count": 0,
                        "planned_count": 0,
                        "dropped_count": 0,
                        "total_pages_read": 0,
                        "total_chapters_read": 0,
                        "total_volumes_read": 0,
                        "mean_score": 0
                    },
                    "overall": {
                        "days_spent_watching": 0,
                        "days_spent_reading": 0,
                        "total_entries": 0,
                        "favorite_genres": []
                    }
                },
                "anime_list": [],
                "manga_list": [],
                "custom_entries": [],  # Ручные добавления
                "reviews": [],
                "favorites": {
                    "anime": [],
                    "manga": [],
                    "characters": []
                },
                "activity_log": []
            }
            self.save_data()
        
        return self.data["users"][user_id_str]
    
    def add_anime(self, user_id: int, anime_data: Dict) -> Dict:
        """Добавляем аниме в список пользователя"""
        user_data = self.get_user_data(user_id)
        
        # Генерируем уникальный ID
        anime_data["id"] = str(uuid.uuid4())[:8]
        anime_data["added_date"] = datetime.now().isoformat()
        anime_data["last_updated"] = datetime.now().isoformat()
        anime_data["type"] = "anime"
        
        # Рассчитываем общее время просмотра
        if anime_data.get("status") == "completed" and anime_data.get("episodes"):
            anime_data["total_duration"] = anime_data.get("duration_per_episode", 24) * anime_data["episodes"]
        elif anime_data.get("status") == "watching" and anime_data.get("watched_episodes"):
            anime_data["total_duration"] = anime_data.get("duration_per_episode", 24) * anime_data["watched_episodes"]
        else:
            anime_data["total_duration"] = 0
        
        user_data["anime_list"].append(anime_data)
        self._update_user_stats(user_id)
        self._log_activity(user_id, f"Добавлено аниме: {anime_data.get('title', 'Unknown')}")
        self.save_data()
        
        return anime_data
    
    def add_manga(self, user_id: int, manga_data: Dict) -> Dict:
        """Добавляем мангу в список пользователя"""
        user_data = self.get_user_data(user_id)
        
        # Генерируем уникальный ID
        manga_data["id"] = str(uuid.uuid4())[:8]
        manga_data["added_date"] = datetime.now().isoformat()
        manga_data["last_updated"] = datetime.now().isoformat()
        manga_data["type"] = "manga"
        
        # Рассчитываем общее количество прочитанных страниц
        if manga_data.get("status") == "completed" and manga_data.get("chapters"):
            manga_data["total_pages"] = manga_data.get("pages_per_chapter", 20) * manga_data["chapters"]
        elif manga_data.get("status") == "reading" and manga_data.get("read_chapters"):
            manga_data["total_pages"] = manga_data.get("pages_per_chapter", 20) * manga_data["read_chapters"]
        else:
            manga_data["total_pages"] = 0
        
        user_data["manga_list"].append(manga_data)
        self._update_user_stats(user_id)
        self._log_activity(user_id, f"Добавлена манга: {manga_data.get('title', 'Unknown')}")
        self.save_data()
        
        return manga_data
    
    def update_anime(self, user_id: int, anime_id: str, update_data: Dict) -> bool:
        """Обновляем данные аниме"""
        user_data = self.get_user_data(user_id)
        
        for anime in user_data["anime_list"]:
            if anime["id"] == anime_id:
                anime.update(update_data)
                anime["last_updated"] = datetime.now().isoformat()
                
                # Пересчитываем время просмотра
                if "status" in update_data or "watched_episodes" in update_data:
                    if anime.get("status") == "completed" and anime.get("episodes"):
                        anime["total_duration"] = anime.get("duration_per_episode", 24) * anime["episodes"]
                    elif anime.get("status") == "watching" and anime.get("watched_episodes"):
                        anime["total_duration"] = anime.get("duration_per_episode", 24) * anime["watched_episodes"]
                
                self._update_user_stats(user_id)
                self._log_activity(user_id, f"Обновлено аниме: {anime.get('title', 'Unknown')}")
                self.save_data()
                return True
        
        return False
    
    def update_manga(self, user_id: int, manga_id: str, update_data: Dict) -> bool:
        """Обновляем данные манги"""
        user_data = self.get_user_data(user_id)
        
        for manga in user_data["manga_list"]:
            if manga["id"] == manga_id:
                manga.update(update_data)
                manga["last_updated"] = datetime.now().isoformat()
                
                # Пересчитываем страницы
                if "status" in update_data or "read_chapters" in update_data:
                    if manga.get("status") == "completed" and manga.get("chapters"):
                        manga["total_pages"] = manga.get("pages_per_chapter", 20) * manga["chapters"]
                    elif manga.get("status") == "reading" and manga.get("read_chapters"):
                        manga["total_pages"] = manga.get("pages_per_chapter", 20) * manga["read_chapters"]
                
                self._update_user_stats(user_id)
                self._log_activity(user_id, f"Обновлена манга: {manga.get('title', 'Unknown')}")
                self.save_data()
                return True
        
        return False
    
    def _update_user_stats(self, user_id: int):
        """Обновляем статистику пользователя"""
        user_data = self.get_user_data(user_id)
        stats = user_data["stats"]
        
        # Статистика аниме
        anime_list = user_data["anime_list"]
        stats["anime"]["total_count"] = len(anime_list)
        stats["anime"]["watching_count"] = len([a for a in anime_list if a.get("status") == "watching"])
        stats["anime"]["completed_count"] = len([a for a in anime_list if a.get("status") == "completed"])
        stats["anime"]["planned_count"] = len([a for a in anime_list if a.get("status") == "planned"])
        stats["anime"]["dropped_count"] = len([a for a in anime_list if a.get("status") == "dropped"])
        stats["anime"]["total_watch_time"] = sum(a.get("total_duration", 0) for a in anime_list)
        
        # Средняя оценка аниме
        rated_anime = [a for a in anime_list if a.get("rating") and a.get("rating") > 0]
        if rated_anime:
            stats["anime"]["mean_score"] = sum(a["rating"] for a in rated_anime) / len(rated_anime)
        
        # Статистика манги
        manga_list = user_data["manga_list"]
        stats["manga"]["total_count"] = len(manga_list)
        stats["manga"]["reading_count"] = len([m for m in manga_list if m.get("status") == "reading"])
        stats["manga"]["completed_count"] = len([m for m in manga_list if m.get("status") == "completed"])
        stats["manga"]["planned_count"] = len([m for m in manga_list if m.get("status") == "planned"])
        stats["manga"]["dropped_count"] = len([m for m in manga_list if m.get("status") == "dropped"])
        stats["manga"]["total_pages_read"] = sum(m.get("total_pages", 0) for m in manga_list)
        stats["manga"]["total_chapters_read"] = sum(m.get("read_chapters", 0) for m in manga_list)
        stats["manga"]["total_volumes_read"] = sum(m.get("read_volumes", 0) for m in manga_list)
        
        # Средняя оценка манги
        rated_manga = [m for m in manga_list if m.get("rating") and m.get("rating") > 0]
        if rated_manga:
            stats["manga"]["mean_score"] = sum(m["rating"] for m in rated_manga) / len(rated_manga)
        
        # Общая статистика
        stats["overall"]["total_entries"] = stats["anime"]["total_count"] + stats["manga"]["total_count"]
        stats["overall"]["days_spent_watching"] = stats["anime"]["total_watch_time"] / (60 * 24)  # минуты -> дни
        stats["overall"]["days_spent_reading"] = stats["manga"]["total_pages_read"] / 100  # пример: 100 страниц в день
        
        # Популярные жанры
        all_genres = []
        for anime in anime_list:
            all_genres.extend(anime.get("genres", []))
        for manga in manga_list:
            all_genres.extend(manga.get("genres", []))
        
        from collections import Counter
        genre_counts = Counter(all_genres)
        stats["overall"]["favorite_genres"] = [genre for genre, count in genre_counts.most_common(5)]
    
    def _log_activity(self, user_id: int, action: str):
        """Логируем активность пользователя"""
        user_data = self.get_user_data(user_id)
        user_data["activity_log"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action
        })
        # Ограничиваем лог последними 100 действиями
        user_data["activity_log"] = user_data["activity_log"][-100:]
    
    def search_user_entries(self, user_id: int, query: str, entry_type: str = "all") -> List[Dict]:
        """Поиск по записям пользователя"""
        user_data = self.get_user_data(user_id)
        results = []
        
        if entry_type in ["all", "anime"]:
            for anime in user_data["anime_list"]:
                if query.lower() in anime.get("title", "").lower():
                    results.append(anime)
        
        if entry_type in ["all", "manga"]:
            for manga in user_data["manga_list"]:
                if query.lower() in manga.get("title", "").lower():
                    results.append(manga)
        
        return results
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Получаем статистику пользователя"""
        user_data = self.get_user_data(user_id)
        return user_data["stats"]

# Создаем глобальный экземпляр базы данных
db = AdvancedDatabase()

# Тестируем базу данных
if __name__ == "__main__":
    test_user_id = 12345
    
    # Тестовые данные аниме
    test_anime = {
        "title": "Человек-бензопила",
        "original_title": "Chainsaw Man",
        "status": "completed",
        "rating": 5,
        "episodes": 12,
        "watched_episodes": 12,
        "duration_per_episode": 24,
        "genres": ["Экшен", "Сёнэн", "Драма"],
        "tags": ["demons", "action", "shounen"],
        "description": "Денджи мечтает о нормальной жизни, но вынужден охотиться на демонов вместе с своим демоном-бензопилой Почитой.",
        "image_url": "",
        "notes": "Отличный экшен!"
    }
    
    # Тестовые данные манги
    test_manga = {
        "title": "Берсерк",
        "original_title": "Berserk",
        "status": "reading",
        "rating": 5,
        "chapters": 400,
        "read_chapters": 347,
        "volumes": 42,
        "read_volumes": 12,
        "pages_per_chapter": 20,
        "genres": ["Фэнтези", "Ужасы", "Драма"],
        "tags": ["dark fantasy", "berserk", "classic"],
        "description": "Мрачная история о воине Гатсе и его борьбе с судьбой.",
        "image_url": "",
        "notes": "Шедевр!"
    }
    
    # Добавляем тестовые данные
    db.add_anime(test_user_id, test_anime)
    db.add_manga(test_user_id, test_manga)
    
    print("🎯 Тест базы данных завершен!")
    print(f"📊 Статистика пользователя: {db.get_user_stats(test_user_id)}")
