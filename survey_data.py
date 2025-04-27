# ====== Import the required modules
import random
import csv
from datetime import datetime, timedelta
import ulid  # For generating ULIDs (requires python-ulid)
from faker import Faker  # For generating fake names

# ====== Initialize Faker for generating fake names
fake = Faker()

# ====== Function to generate ULID-based customer identifier
def generate_customer_number():
    return str(ulid.ULID())  # Generates a ULID as a string

# ====== Function to generate random order number (up to 5 digits)
def generate_order_number():
    return random.randint(1, 99999)

# ====== Function to generate random date between start_date and end_date
def generate_random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# ====== Function to generate mock customer response based on an NPS score
def generate_customer_response(nps_score):
    topics = {
        1: [
            "Outstanding customer service, staff went above and beyond to help me find the right gear.",
            "Best prices I’ve seen for high-quality fishing rods, no complaints here!",
            "Product was in stock and worked perfectly, couldn’t be happier.",
            "Fast shipping on my online order, arrived ahead of schedule.",
            "Return process was super easy and hassle-free.",
            "Knowledgeable staff helped me pick the perfect hunting boots."
        ],
        2: [
            "Good pricing on camping gear, but the checkout line took forever.",
            "Reliable product, though the staff seemed too busy to assist.",
            "Decent selection, but I wish they had more sizes in stock.",
            "Customer service was friendly but not very knowledgeable about firearms.",
            "Business hours are convenient, but the store was a bit messy.",
            "Online order arrived on time, but packaging was slightly damaged."
        ],
        3: [
            "Average experience, pricing was okay but nothing special.",
            "Product availability was hit or miss, had to settle for my second choice.",
            "Customer service was fine but didn’t seem to care much.",
            "Store was clean, but the return policy felt restrictive.",
            "Shipping took longer than expected for my kayak order.",
            "Business hours are alright, but they close too early on weekends."
        ],
        4: [
            "Poor product availability, they were out of the tent I wanted.",
            "Hidden fees popped up at checkout, really soured the experience.",
            "Customer service was slow and unhelpful with my warranty question.",
            "Unreliable product—my reel broke after one fishing trip.",
            "Store hours are inconvenient, closed when I needed to shop.",
            "Online order was delayed with no updates, frustrating process."
        ],
        5: [
            "Terrible customer service, staff ignored me while I waited for help.",
            "Hidden fees everywhere, felt like a bait-and-switch on pricing.",
            "Product was defective—my bike tire popped on the first ride.",
            "Return policy is a nightmare, they wouldn’t take back a faulty item.",
            "Out of stock on half the fishing gear I needed, waste of a trip.",
            "Business hours are ridiculous, closed mid-day when I stopped by.",
            "Online order lost in transit and no one could explain why."
        ]
    }
    num_issues = random.randint(1, 3)
    selected_topics = random.sample(topics[nps_score], min(num_issues, len(topics[nps_score])))
    return " and ".join(selected_topics) + ".", selected_topics

# ====== Function to generate churn reason based on customer response
def generate_churn_reason(selected_topics):
    # Map customer response topics to corresponding churn reasons (only the part after the colon)
    churn_reasons = {
        # NPS 3
        "Average experience, pricing was okay but nothing special.":
            "more competitive pricing and better value",
        "Product availability was hit or miss, had to settle for my second choice.":
            "the exact products I needed in stock",
        "Customer service was fine but didn’t seem to care much.":
            "more attentive and caring customer support",
        "Store was clean, but the return policy felt restrictive.":
            "a more flexible and customer-friendly return policy",
        "Shipping took longer than expected for my kayak order.":
            "faster and more reliable shipping",
        "Business hours are alright, but they close too early on weekends.":
            "more convenient store hours, including extended weekend availability",
        # NPS 4
        "Poor product availability, they were out of the tent I wanted.":
            "better stock and availability for camping gear",
        "Hidden fees popped up at checkout, really soured the experience.":
            "transparent pricing and no hidden fees",
        "Customer service was slow and unhelpful with my warranty question.":
            "faster and more helpful warranty support",
        "Unreliable product—my reel broke after one fishing trip.":
            "more durable and reliable products",
        "Store hours are inconvenient, closed when I needed to shop.":
            "more flexible store hours that fit my schedule",
        "Online order was delayed with no updates, frustrating process.":
            "timely order updates and faster delivery",
        # NPS 5
        "Terrible customer service, staff ignored me while I waited for help.":
            "responsive and attentive customer service",
        "Hidden fees everywhere, felt like a bait-and-switch on pricing.":
            "clear, upfront pricing and no surprises",
        "Product was defective—my bike tire popped on the first ride.":
            "higher-quality products that I can rely on",
        "Return policy is a nightmare, they wouldn’t take back a faulty item.":
            "a straightforward and fair return process",
        "Out of stock on half the fishing gear I needed, waste of a trip.":
            "the fishing gear I need in stock",
        "Business hours are ridiculous, closed mid-day when I stopped by.":
            "more convenient and predictable hours",
        "Online order lost in transit and no one could explain why.":
            "reliable order tracking and delivery"
    }
    # Select one churn reason based on the first applicable topic
    for topic in selected_topics:
        if topic in churn_reasons:
            return churn_reasons[topic]
    # Fallback if no specific reason matches
    return "a better overall experience"

# ====== Set start_date and end_date
start_date = datetime.now().date().replace(month=1, day=1)  # First day of current year
end_date = datetime.now().date()  # Today's date

# ====== Generate 205 randomly populated rows of customer comments
data = []
for _ in range(205):
    # Generate NPS score (1–5)
    nps_score = random.randint(1, 5)
    order_date = generate_random_date(start_date, end_date).strftime('%Y-%m-%d')
    survey_date = generate_random_date(start_date, end_date).strftime('%Y-%m-%d')

    # Generate customer response and get selected topics for churn reason
    customer_response, selected_topics = generate_customer_response(nps_score)

    # Determine churn status: only allow churn for NPS 3, 4, or 5 (20% chance)
    churned = 0
    if nps_score in [3, 4, 5]:
        churned = random.choices([0, 1], weights=[0.8, 0.2], k=1)[0]

    # Generate churn_date and churn_reason if churned, else empty
    churn_date = ""
    churn_reason = ""
    if churned:
        churn_date = generate_random_date(start_date, end_date).strftime('%Y-%m-%d')
        churn_reason = generate_churn_reason(selected_topics)

    row = [
        generate_customer_number(),
        fake.first_name(),
        fake.last_name(),
        generate_order_number(),
        order_date,
        nps_score,
        customer_response,
        survey_date,
        churned,
        churn_date,
        churn_reason
    ]
    data.append(row)

# ====== Write the data to a CSV
with open('nps_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Customer Number', 'First Name', 'Last Name', 'Order Number', 'Order Date',
                     'NPS Score', 'Customer Response', 'Survey Date', 'Churned', 'Churn Date', 'Churn Reason'])
    writer.writerows(data)

print("CSV file 'nps_data.csv' has been generated.")