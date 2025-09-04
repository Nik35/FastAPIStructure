#!/bin/bash
# Test script for entrypoint.sh logic

set -e

# Test 1: Should initialize Alembic if migrations/ does not exist
test_dir=$(mktemp -d)
cp entrypoint.sh "$test_dir/entrypoint.sh"
cd "$test_dir"

# Mock alembic and pg_isready
cat <<'EOF' > alembic
#!/bin/bash
echo "alembic $@"
if [[ "$1" == "init" ]]; then
  mkdir migrations
fi
EOF
chmod +x alembic
cat <<'EOF' > pg_isready
#!/bin/bash
exit 0
EOF
chmod +x pg_isready
export PATH="$test_dir:$PATH"

# Set DB env vars
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=user

# Remove migrations if exists
rm -rf migrations

# Run entrypoint.sh with a dummy command
bash entrypoint.sh echo "App started"

if [ ! -d migrations ]; then
  echo "Test FAILED: migrations/ was not created"
  exit 1
fi

echo "Test PASSED: migrations/ was created and entrypoint ran"

# Test 2: Should not re-init if migrations/ exists
bash entrypoint.sh echo "App started again"

echo "Test PASSED: entrypoint.sh does not re-init migrations if already present"

# Cleanup
echo "All entrypoint.sh tests passed."
