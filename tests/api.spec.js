import { test, expect } from '@playwright/test';

const baseURL = 'http://localhost:8003';
const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ1c2VyX2lkIjoyLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MTI0NTc3MCwidHlwZSI6ImFjY2VzcyJ9.wIW_klDQvqszjUAbPn0NM0H2SIP7oXwuxQZauU_AwJA';
let passenger_id;
let token;

const newBooking = {
  firstname: 'Jack',
  lastname: 'Dawson',
  age: 20,
  destination: "Pursue dreams in America",
  embarked: "Southampton",
  fare: 8.05,
  name: " Mr. Jack",
  pclass: 3,
  sex: "male",
  ticket: "A/5 21171",
};

const updatedBooking = {
  firstname: 'DeWitt Bukater, Miss. Rose',
  age: 17,
  destination: "New York",
  embarked: "SouthHampton",
  fare: 211.34,
  name: " Mr. James",
  pclass: 1,
  sex: "female",
  ticket: "PC 17599",
  cabin: "B52",
};


test.describe('API-тесты для Titanic @api', () => {
  test.beforeAll(async ({ request }) => {
    // 1. Создание нового бронирования
    const createResp = await request.post(`${baseURL}/passengers`, {
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: newBooking,
    });

    expect(createResp.status()).toBe(201);
    const body = await createResp.json();
    
    expect(body).toHaveProperty('passenger_id');
    passenger_id = body.passenger_id;
    token = AUTH_TOKEN;
  });

 test('Чтение бронирования', async ({ request }) => {
    const resp = await request.get(`${baseURL}/passengers/${newBooking.lastname}`);
    
    expect(resp.status()).toBe(200);

    const data = await resp.json();
    expect(data.firstname).toBe(newBooking.firstname);
    expect(data.lastname).toBe(newBooking.lastname);
});

   test('Обновление бронирования', async ({ request }) => {
    const resp = await request.put(`${baseURL}/passengers/${passenger_id}`, {
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      data: updatedBooking,
    });

    expect(resp.status()).toBe(200);
    const updated = await resp.json();
    
    expect(updated).toMatchObject(updatedBooking);
});
});
