#!/bin/bash
# Migration script for PythonAnywhere server
# Run this script after pulling new code: bash run_migration.sh

echo "🔄 Running database migration for attendance feature..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check Flask is installed
if ! command -v flask &> /dev/null; then
    echo "❌ Flask not found. Install requirements:"
    echo "   pip install -r requirements.txt"
    exit 1
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
