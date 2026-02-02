#!/bin/bash
# Migration script for PythonAnywhere server
# Run this script after pulling new code: bash run_migration.sh

echo "🔄 Running database migration for attendance feature..."
echo ""

# Try to find and activate virtual environment
VENV_ACTIVATED=false

# Check common virtual environment locations
if [ -d "venv" ]; then
    echo "📦 Found virtual environment: venv"
    source venv/bin/activate
    VENV_ACTIVATED=true
elif [ -d "env" ]; then
    echo "📦 Found virtual environment: env"
    source env/bin/activate
    VENV_ACTIVATED=true
elif [ -d "../venv" ]; then
    echo "📦 Found virtual environment: ../venv"
    source ../venv/bin/activate
    VENV_ACTIVATED=true
else
    echo "⚠️  No virtual environment found, trying without..."
fi

# Check Flask is installed
if ! command -v flask &> /dev/null; then
    echo "❌ Flask not found."
    echo ""
    echo "💡 Please run manually:"
    echo "   source /path/to/your/venv/bin/activate"
    echo "   flask db upgrade"
    exit 1
fi

if [ "$VENV_ACTIVATED" = true ]; then
    echo "✅ Virtual environment activated"
fi

echo "📦 Current migration status:"
flask db current

echo ""
echo "🔄 Upgrading database..."
flask db upgrade

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📊 New migration applied:"
    echo "   - Added 'attendance' table"
    echo "   - Students can be marked Present/Absent daily"
    echo "   - Parents receive notifications for absences"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to PythonAnywhere Web tab"
    echo "2. Click the green 'Reload' button"
    echo "3. Test the attendance feature at /admin/attendance"
    echo ""
else
    echo ""
    echo "❌ Migration failed. Check the error above."
    echo ""
    echo "💡 Common fixes:"
    echo "   - Make sure database file is writable"
    echo "   - Check if migrations folder exists"
    echo "   - Try: flask db stamp head (if table already exists)"
    exit 1
fi
