# 看服务状态
docker compose ps

# 看日志
docker compose logs -f backend

# 停止服务但保留数据库数据
docker compose down

# 停止服务并删除 PostgreSQL 数据，慎用
docker compose down -v

docker compose up -d postgres redis
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m app.db.init_db
docker compose up -d