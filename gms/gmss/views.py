from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
# Create your views here.
from django.contrib import messages
def home(request):
    if request.method=='POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        mobile=request.POST.get('mobile')
        message=request.POST.get('message')
        if name and email and mobile and message:
            Enquiry.objects.create(name=name,email=email,mobile=mobile,message=message)
            messages.success(request,'Your enquiry has been successfully!')
            return render(request,'home.html')
        else:
            messages.error(request,'Please fill in all fields.')
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')

from django.contrib.auth import authenticate,login,logout
def admin_login_views(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None and getattr(user,'role'):
            login(request,user)
            messages.success(request,'LOgged in successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request,'Invalid credentials or not an admin.')
    return render(request,'admin_login.html')



def admin_required(view_func):
    def wrapper(request,*args,**kwargs):
        if (not request.user.is_authenticated) or (getattr(request.user,'role',None) != 'ADMIN'):
            messages.error(request,'You must be an admin to access this page.')
            return redirect('admin_login')
        return view_func(request,*args,**kwargs)
    return wrapper

def member_required(view_func):
    def wrapper(request,*args,**kwargs):
        if (not request.user.is_authenticated) or (getattr(request.user,'role',None) != 'MEMBER'):
            messages.error(request,'You must be an member to access this page.')
            return redirect('member_login')
        return view_func(request,*args,**kwargs)
    return wrapper


def member_login_views(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None and getattr(user,'role'):
            login(request,user)
            messages.success(request,'LOgged in successfully!')
            return redirect('member_dashboard')
        else:
            messages.error(request,'Invalid credentials or not an member.')
    return render(request,'member_login.html')


def member_dashboard_views(request):
    member=request.user.member_profile
    total_attendance=member.attendances.count()
    total_payments=member.payments.count()
    workout_count=member.workout_plans.count()

    return render(request,'member_dashboard.html',{'member':member,'total_attendance':total_attendance,'total_payments':total_payments,'workout_count':workout_count})

@member_required
def member_feedback(request):
    member=request.user.member_profile
    if request.method=='POST':
        message=request.POST.get('message')
        if message:
            Feedback.objects.create(member=member,message=message)
            messages.success(request,'Your Feedback has been submitted successfully!')
            return redirect('member_feedback')
        else:
            messages.error(request,'Please enter your feedback before submitting.')
    feedbacks=member.feedbacks.all().order_by('-created_at')
    return render(request,'member_feedback.html',{'feedbacks':feedbacks})


@admin_required
def admin_dashboard_views(request):
    total_members=MemberProfile.objects.count()
    active_membership=MemberProfile.objects.filter(membership_end__gte=timezone.now().date()).count()
    total_registrations=MemberProfile.objects.filter(join_date=timezone.now().date()).count()
    pending_payments=Payment.objects.filter(status='PENDING').count()

    return render(request,'admin_dashboard.html',{'total_members':total_members,'active_membership':active_membership,'total_registrations':total_registrations,'pending_payments':pending_payments})


def logout_views(request):
    logout(request)
    messages.info(request,'Logged Out Successfully.')
    return redirect('home')

@admin_required
def admin_plans_list(request):
    plans=MembershipPlan.objects.all().order_by('duration_months')
    return render(request,'admin_plans_list.html',{'plans':plans})

@admin_required
def admin_plan_add(request):
    if request.method=='POST':
        name=request.POST.get('name')
        duration_months=request.POST.get('duration_months')
        fee=request.POST.get('fee')
        description=request.POST.get('description')

        if name and duration_months and fee:
            MembershipPlan.objects.create(name=name,duration_months=duration_months,fee=fee,description=description)
            messages.success(request,'Membership plan added successfully!')
            return redirect('admin_plans_list')
        else:
            messages.error(request,'Please fill in all mentioned fields.!')
    return render(request,'admin_plan_form.html',{'mode':'add'})


@admin_required
def admin_plan_edit(request,plan_id):
    plan=MembershipPlan.objects.get(id=plan_id)
    if request.method=='POST':
        name=request.POST.get('name')
        duration_months=request.POST.get('duration_months')
        fee=request.POST.get('fee')
        description=request.POST.get('description')

        if name and duration_months and fee:
            plan.name=name
            plan.duration_months=duration_months
            plan.fee=fee
            plan.description=description
            plan.save()
            messages.success(request,'Membership plan updated successfully!')
            return redirect('admin_plans_list')
        else:
            messages.error(request,'Please fill in all fields.!')
    return render(request,'admin_plan_form.html',{'plan':plan,'mode':'edit'})


@admin_required
def admin_plan_delete(request,plan_id):
    plan=MembershipPlan.objects.get(id=plan_id)
    if request.method=='POST':
        plan.delete()
        messages.success(request,'Membership plan deleted successfully!')
        return redirect('admin_plans_list')
    return redirect('admin_plans_list')



@admin_required
def admin_trainers_list(request):
    trainers=Trainer.objects.all().order_by('name')
    return render(request,'admin_trainers_list.html',{'trainers':trainers})


@admin_required
def admin_trainer_add(request):
    if request.method=='POST':
        name=request.POST.get('name')
        mobile=request.POST.get('mobile')
        specialization=request.POST.get('specialization')
        shift_timing=request.POST.get('shift_timing')
    
        if name and mobile and specialization and shift_timing:
            Trainer.objects.create(name=name,mobile=mobile,specialization=specialization,shift_timing=shift_timing)
            messages.success(request,'Trainer added successfully!')
            return redirect('admin_trainers_list')
        else:
            messages.error(request,'Please fill in all mentioned fields.!')
    return render(request,'admin_trainer_form.html',{'mode':'add'})


@admin_required
def admin_trainer_edit(request,trainer_id):
    trainer=Trainer.objects.get(id=trainer_id)
    if request.method=='POST':
        name=request.POST.get('name')
        mobile=request.POST.get('mobile')
        specialization=request.POST.get('specialization')
        shift_timing=request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            trainer.name=name
            trainer.mobile=mobile
            trainer.specialization=specialization
            trainer.shift_timing=shift_timing
            trainer.save()
            messages.success(request,'trainer updated successfully!')
            return redirect('admin_trainers_list')
        else:
            messages.error(request,'Please fill in all fields.!')
    return render(request,'admin_trainer_form.html',{'trainer':trainer,'mode':'edit'})


@admin_required
def admin_trainer_delete(request,trainer_id):
    trainer=Trainer.objects.get(id=trainer_id)
    if request.method=='POST':
        trainer.delete()
        messages.success(request,'Trainer deleted successfully!')
        return redirect('admin_trainers_list')
    return redirect('admin_trainers_list')


@admin_required
def admin_members_list(request):
    search=request.GET.get('search','')
    members=MemberProfile.objects.all().select_related('user','plan')
    if search:
        members=members.filter(full_name__icontains=search)
    return render(request,'admin_members_list.html',{'members':members,'search':search})


@admin_required
def admin_member_add(request):
    plans=MembershipPlan.objects.all().order_by('duration_months')
    trainers=Trainer.objects.all().order_by('name')
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        full_name=request.POST.get('full_name')
        mobile=request.POST.get('mobile')
        age=request.POST.get('age')
        gender=request.POST.get('gender')
        address=request.POST.get('address')
        join_date=request.POST.get('join_date') or timezone.now().date()
        plan_id=request.POST.get('plan_id')
        trainer_id=request.POST.get('trainer_id')

        if User.objects.filter(username=username).exists():
            messages.error(request,'Username already exists. Please choose a different username.')
            return redirect('admin_member_add')

        user=User.objects.create_user(username=username,password=password,role='MEMBER')
        plan=None
        if plan_id:
            plan=MembershipPlan.objects.get(id=plan_id)
        trainer=None
        if trainer_id:
            trainer=Trainer.objects.get(id=trainer_id)
        MemberProfile.objects.create(user=user,full_name=full_name,mobile=mobile,age=age,gender=gender,address=address,join_date=join_date,plan=plan,trainer=trainer)
        messages.success(request,'Member added successfully!')
        return redirect('admin_members_list')
    return render(request,'admin_member_form.html',{'plans':plans,'trainers':trainers,'mode':'add'})


@admin_required
def admin_member_edit(request,member_id):
    member=MemberProfile.objects.get(id=member_id)
    plans=MembershipPlan.objects.all().order_by('duration_months')
    trainers=Trainer.objects.all().order_by('name')
    if request.method=='POST':
        full_name=request.POST.get('full_name')
        mobile=request.POST.get('mobile')
        age=request.POST.get('age')
        gender=request.POST.get('gender')
        address=request.POST.get('address')
        join_date=request.POST.get('join_date') or member.join_date
        plan_id=request.POST.get('plan_id')
        trainer_id=request.POST.get('trainer_id')

        plan=MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer=Trainer.objects.get(id=trainer_id) if trainer_id else None

        member.full_name=full_name
        member.mobile=mobile
        member.age=age
        member.gender=gender
        member.address=address
        member.join_date=join_date
        member.plan=plan
        member.trainer=trainer
        member.save()
        messages.success(request,'Member Updated successfully!')
        return redirect('admin_members_list')
    return render(request,'admin_member_form.html',{'member':member,'plans':plans,'trainers':trainers,'mode':'edit'})

@admin_required
def admin_member_delete(request,member_id):
    member=MemberProfile.objects.get(id=member_id)
    if request.method=='POST':
        user=member.user
        member.delete()
        user.delete()
        messages.success(request,'Member deleted successfully!')
        return redirect('admin_members_list')
    return redirect('admin_members_list')



@admin_required
def admin_attendance_list(request):
    today=timezone.now().date()
    date=request.GET.get('date',today)
    
    attendances=Attendance.objects.all().select_related('member').filter(date=date)
    members=MemberProfile.objects.all().order_by('full_name')
    member_id=request.GET.get('member_id')
    if member_id:
        attendances=attendances.filter(member_id=member_id)


    return render(request,'admin_attendance_list.html',{'attendances':attendances,'members':members,'today':today,'selected_member_id':member_id,'selected_date':date})


@admin_required
def admin_attendance_add(request):
    members=MemberProfile.objects.all().order_by('full_name')

    if request.method=='POST':
        member_id=request.POST.get('member_id')
        date=request.POST.get('date')
        time_in=request.POST.get('time_in')

        if not member_id:
            messages.error(request,'Please select a member.')
            return redirect('admin_attendance_add')
        member=MemberProfile.objects.get(id=member_id)

        attendance,created=Attendance.objects.get_or_create(
            member=member,date=date
        )
        attendance.time_in=time_in
        attendance.save()
        if created:
            messages.success(request,'Attendance recorded successfully!')
        else:
            messages.info(request,'Attendance updated successfully!')
        return redirect('admin_attendance_add')
    return render(request,'admin_attendance_form.html',{'members':members})



@admin_required
def admin_equipment_list(request):
    equipments=Equipment.objects.all().order_by('name')
    return render(request,'admin_equipment_list.html',{'equipments':equipments})


@admin_required
def admin_equipment_add(request):
    if request.method=='POST':
        name=request.POST.get('name')
        units=request.POST.get('units')
        price=request.POST.get('price')
        purchase_date=request.POST.get('purchase_date') or timezone.now().date()

        if name and units and price:
            Equipment.objects.create(name=name,units=units,price=price,purchase_date=purchase_date)
            messages.success(request,'Equipment added successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request,'please fill in all fields.')
    return render(request,'admin_equipment_form.html',{'mode':'add'})

@admin_required
def admin_equipment_edit(request,equipment_id):
    equipment=Equipment.objects.get(id=equipment_id)
    if request.method=='POST':
        name=request.POST.get('name')
        units=request.POST.get('units')
        price=request.POST.get('price')
        # purchase_date=request.POST.get('purchase_date') or equipment.purchase_date=purchase_date
        purchase_date=request.POST.get('purchase_date')

        if name and units and price:
            equipment.name=name
            equipment.units=units
            equipment.price=price
            if purchase_date:
                equipment.purchase_date=purchase_date
            equipment.save()
            messages.success(request,'Equipment Updated successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request,'please fill all fields!.')
    return render(request,'admin_equipment_form.html',{'equipment':equipment,'mode':'edit'})

@admin_required
def admin_equipment_delete(request,equipment_id):
    equipment=Equipment.objects.get(id=equipment_id)
    if request.method=='POST':
        equipment.delete()
        messages.success(request,'Equipment deleted successfullyy!..')
        return redirect('admin_equipment_list')
    return redirect('admin_equipment_list')


@admin_required
def admin_enquiries_list(request):
    enquiries=Enquiry.objects.all().order_by('-created_at')
    return render(request,'admin_enquiries_list.html',{'enquiries':enquiries})

@admin_required
def admin_enquiry_update_status(request,enquiry_id):
    if request.method=='POST':
        status=request.POST.get('status')
        enquiry=Enquiry.objects.get(id=enquiry_id)
        if status in ['NEW','SEEN','RESOLVED']:
            enquiry.status=status
            enquiry.save()
            messages.success(request,'Enquiry Stauts Updated !..')
    return redirect('admin_enquiries_list')


@admin_required
def admin_workout_plans_list(request):
    member_id=request.GET.get('member_id')

    workout_plans=WorkoutPlan.objects.select_related('member').all().order_by('-created_at')
    if member_id:
        workout_plans=workout_plans.filter(member__id=member_id)
    members=MemberProfile.objects.all().order_by('full_name')
    return render(request,'admin_workout_plans_list.html',{'workout_plans':workout_plans,'members':members,'selected_member_id':member_id})

@admin_required
def admin_workout_plan_add(request):
    members=MemberProfile.objects.all().order_by('full_name')
    if request.method=='POST':
        member_id=request.POST.get('member_id')
        title=request.POST.get('title')
        description=request.POST.get('description')

        if not member_id or not title or not description:
            messages.error(request,'please select a member and enter plan details.')
            return redirect('admin_workout_plan_add')
        member=MemberProfile.objects.get(id=member_id)

        WorkoutPlan.objects.create(member=member,title=title,description=description)
        messages.success(request,'WorkOut Plan Added successfully!')
        return redirect('admin_workout_plans_list')
    return render(request,'admin_workout_plan_form.html',{'members':members})




@admin_required
def admin_workout_plan_delete(request,plan_id):
    plan=WorkoutPlan.objects.get(id=plan_id)
    if request.method=='POST':
        plan.delete()
        messages.success(request,'Workout plan deleted successfully!')
        return redirect('admin_workout_plans_list')
    return redirect('admin_workout_plans_list')


@admin_required
def admin_payments_list(request):
    member_id=request.GET.get('member_id')
    status=request.GET.get('status')
    payments=Payment.objects.select_related('member','plan').all().order_by('-payment_date')
    if member_id:
        payments=payments.filter(member__id=member_id)
    if status in ['PENDING','PAID']:
        payments=payments.filter(status=status)
    members=MemberProfile.objects.all().order_by('full_name')
    return render(request,'admin_payments_list.html',{'payments':payments,'members':members,'selected_member_id':member_id,'selected_status':status})


from datetime import datetime

@admin_required
def admin_payment_add(request):

    members = MemberProfile.objects.all().order_by('full_name')
    plans = MembershipPlan.objects.all().order_by('duration_months')

    if request.method == 'POST':

        member_id = request.POST.get('member_id')
        plan_id = request.POST.get('plan_id')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date') or timezone.now().date()
        mode = request.POST.get('mode')
        notes = request.POST.get('notes')
        status = request.POST.get('status')

        set_membership = request.POST.get('set_membership')
        membership_start = request.POST.get('membership_start')

        # Required fields
        if not member_id or not plan_id or not amount or not status:

            messages.error(
                request,
                'Please fill all required fields!'
            )

            return redirect('admin_payment_add')

        # Get member and plan
        member = MemberProfile.objects.get(id=member_id)
        plan = MembershipPlan.objects.get(id=plan_id)

        # Payment validation
        if plan and plan.fee:

            total_paid = Payment.objects.filter(
                member=member,
                plan=plan,
                status='PAID'
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or 0

            total_paid = float(total_paid)
            amount = float(amount)
            plan_fee = float(plan.fee)

            remaining_amount = plan_fee - total_paid
            new_total = total_paid + amount

            if new_total > plan_fee:

                excess_amount = new_total - plan_fee

                messages.error(
                    request,
                    f'Plan fee: ₹{plan_fee}. '
                    f'Already paid: ₹{total_paid}. '
                    f'Remaining amount: ₹{remaining_amount}. '
                    f'You entered ₹{amount}, which exceeds the remaining amount '
                    f'by ₹{excess_amount}.'
                )

                return redirect('admin_payment_add')

        # Create payment
        Payment.objects.create(
            member=member,
            plan=plan,
            amount=amount,
            status=status,
            mode=mode,
            payment_date=payment_date,
            notes=notes
        )

        # Update membership
        if set_membership == 'on' and plan and membership_start:

            membership_start = datetime.strptime(
                membership_start,
                '%Y-%m-%d'
            ).date()

            member.plan = plan
            member.membership_start = membership_start

            member.membership_end = (
                membership_start +
                timezone.timedelta(
                    days=plan.duration_months * 30
                )
            )

            member.save()

        messages.success(
            request,
            'Payment Recorded successfully!'
        )

        return redirect('admin_payments_list')

    return render(
        request,
        'admin_payment_form.html',
        {
            'members': members,
            'plans': plans
        }
    )



@member_required
def member_attendance(request):
    member_profile=MemberProfile.objects.get(user=request.user)
    attendances=Attendance.objects.filter(member=member_profile).order_by('-date')
    return render(request,'member_attendance.html',{'attendances':attendances})


@member_required
def member_membership(request):
    member=request.user.member_profile

    days_remaining=None
    total_paid=0
    remaining=None
    membership_status=None

    if member.membership_end:
        days_remaining=(member.membership_end - timezone.now().date()).days

        if days_remaining <= 0:
            days_remaining = 0
            membership_status= 'Membership Ended'
        else:
            membership_status='Active'
    if member.plan:
        agg=Payment.objects.filter(member=member,plan=member.plan,status='PAID').aggregate(total=models.Sum('amount'))

        total_paid=agg['total'] or 0

        if member.plan.fee:
            remaining=float(member.plan.fee) - float(total_paid)
    context = {
        'member':member,
        'membership_status':membership_status,
        'days_remaining':days_remaining,
        'total_paid':total_paid,
        'remaining':remaining
    }
    return render(request,'member_membership.html',context)



@member_required
def member_payments_list(request):
    member_profile=MemberProfile.objects.get(user=request.user)
    payments=Payment.objects.filter(member=member_profile).order_by('-payment_date')
    return render(request,'member_payments.html',{'payments':payments})

@member_required
def member_workout_plans(request):
    member_profile=MemberProfile.objects.get(user=request.user)
    workout_plans=WorkoutPlan.objects.filter(member=member_profile).order_by('-created_at')
    return render(request,'member_workout_plans.html',{'workout_plans':workout_plans})


@member_required
def member_profile(request):
    member=request.user.member_profile
    return render(request,"member_profile.html",{'member':member})

@member_required
def member_profile_edit(request):
    member=request.user.member_profile
    if request.method == 'POST':
        member.full_name=request.POST.get('full_name')
        member.mobile=request.POST.get('mobile')
        member.age=request.POST.get('age')
        member.gender=request.POST.get('gender')
        member.address=request.POST.get('address')
        member.save()
        messages.success(request,'Profile Updated Successfully!..')
        return redirect('member_profile')
    return render(request,'member_profile_edit.html',{'member':member})

@member_required
def member_change_password(request):
    if request.method=='POST':
        current_password=request.POST.get('current_password')
        new_password=request.POST.get('new_password')
        confirm_password=request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request,'Current password is incorrect.')
            return redirect('member_change_password')

        if new_password != confirm_password:
            messages.error(request,'New Password and confirm password do not match.')
            return redirect('member_change_password')
        request.user.set_password(new_password)  
        request.user.save()
        messages.success(request,'Password changed successfully ! please log in again')
        return redirect('member_login')
    return render(request,'member_change_password.html')



# @member_required
def admin_feedbacks_list(request):
    member_id=request.GET.get('member_id')
    feedbacks=Feedback.objects.select_related('member').all().order_by('-created_at')
    members=MemberProfile.objects.all().order_by('full_name')
    if member_id:
        feedbacks=feedbacks.filter(member_id=member_id)
    context={
        'feedbacks':feedbacks,
        'members':members,
        'selected_member_id':int(member_id) if member_id else None,
    }
    return render(request,'admin_feedbacks_list.html',context)
