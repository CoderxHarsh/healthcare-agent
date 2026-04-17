import asyncio
from database import AsyncSessionLocal
from models import User
from sqlalchemy.future import select

async def check_user_data():
    """Check if user onboarding data is stored in database"""
    async with AsyncSessionLocal() as db:
        try:
            # Get all users
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("❌ No users found in database")
                return
            
            print("\n" + "="*80)
            print("📊 USER ONBOARDING DATA IN DATABASE")
            print("="*80 + "\n")
            
            for user in users:
                print(f"👤 User: {user.email}")
                print(f"   ID: {user.id}")
                print(f"   Name: {user.name}")
                print(f"   Created: {user.created_at}")
                print(f"   Last Login: {user.last_login_at}")
                print(f"   Is Onboarded: {'✅ YES' if user.is_onboarded else '❌ NO'}")
                print(f"   Onboarded At: {user.onboarded_at if user.onboarded_at else 'Not set'}")
                
                # Check if onboarding fields are filled
                print(f"\n   📋 Health Profile:")
                print(f"      • Age: {user.age if user.age else '❌ Not set'}")
                print(f"      • Gender: {user.gender if user.gender else '❌ Not set'}")
                print(f"      • Height: {user.height_cm if user.height_cm else '❌ Not set'} cm")
                print(f"      • Weight: {user.weight_kg if user.weight_kg else '❌ Not set'} kg")
                print(f"      • Health Conditions: {user.health_conditions if user.health_conditions else '❌ Not set'}")
                print(f"      • Medications: {user.medications if user.medications else '❌ Not set'}")
                print(f"      • Allergies: {user.allergies if user.allergies else '❌ Not set'}")
                print(f"      • Fitness Level: {user.fitness_level if user.fitness_level else '❌ Not set'}")
                print(f"      • Health Goals: {user.health_goals if user.health_goals else '❌ Not set'}")
                
                # Summary
                print(f"\n   ✨ SUMMARY:")
                onboarding_fields = [
                    user.age,
                    user.gender,
                    user.height_cm,
                    user.weight_kg,
                    user.fitness_level
                ]
                filled_fields = sum(1 for field in onboarding_fields if field)
                print(f"      Profile Completion: {filled_fields}/5 core fields filled")
                
                if filled_fields == 5 and user.is_onboarded:
                    print(f"      Status: ✅ ONBOARDING COMPLETE & DATA SAVED")
                elif filled_fields == 5:
                    print(f"      Status: ⚠️  DATA SAVED BUT NOT MARKED COMPLETE")
                elif filled_fields > 0:
                    print(f"      Status: ⏳ PARTIAL DATA SAVED")
                else:
                    print(f"      Status: ❌ NO ONBOARDING DATA SAVED")
                
                print("\n" + "-"*80 + "\n")
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")

if __name__ == "__main__":
    print("🔄 Checking user onboarding data in database...\n")
    asyncio.run(check_user_data())
