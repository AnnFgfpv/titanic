import { test, expect } from '@playwright/test';

const baseURL = 'http://localhost:8003';
const AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJteXVzZXIiLCJ1c2VyX2lkIjoyLCJyb2xlIjoidXNlciIsImV4cCI6MTc2MTI0NTc3MCwidHlwZSI6ImFjY2VzcyJ9.wIW_klDQvqszjUAbPn0NM0H2SIP7oXwuxQZauU_AwJA';
let passenger_id;
let token;

const newBooking = {
  name: "Dawson, Mr. Jack",
  age: 20,
  destination: "Pursue dreams in America",
  embarked: "Southampton",
  fare: 8.05,
  pclass: 3,
  cabin: null,
  sex: "male",
  ticket: "A/5 21171",
  passenger_id: 101,
};

const updatedBooking = {
  name: "DeWitt Bukater, Miss. Rose",
  age: 17,
  destination: "Wedding in Philadelphia",
  embarked: "SouthHampton",
  fare: 512.3292,
  pclass: 1,
  sex: "female",
  ticket: "PC 17599",
  cabin: "B52",
  passenger_id: 102,
};



test.describe('API-тесты для Titanic @api', () => {
  test.beforeAll(async ({ request }) => {
    // 1. Создание нового бронирования
    const createResp = await request.post(`${baseURL}/passengers`, {
      headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      data: newBooking,
    });

    expect(createResp.status()).toBe(201);
    const body = await createResp.json();
    
    expect(body).toHaveProperty('passenger_id');
    passenger_id = body.passenger_id;
    token = AUTH_TOKEN;
  });

 test('Поиск пассажиров по имени', async ({ request }) => {
    const resp = await request.get(`${baseURL}/passengers/search/${newBooking.name}`, {
        headers: {
        'Accept': 'application/json'
         }
        });
    
    expect(resp.status()).toBe(200);

    const data = await resp.json();
    expect(data.name).toBe(newBooking.name);
});

   test('Получить пассажира по id', async ({ request }) => {
    const resp = await request.get(`${baseURL}/passengers/${updatedBooking.passenger_id}`, {
      headers: {
     'Accept': 'application/json'
      }
    });

    expect(resp.status()).toBe(200);
    const updated = await resp.json();
    
    expect(updated.passenger_id).toBe(updatedBooking.passenger_id);
});

test ('Обновление данные пассажира', async ({ request }) => {
    const resp = await request.put(`${baseURL}/passengers/${updatedBooking.passenger_id}`, {
        headers: {
        'Authorization': `Bearer ${AUTH_TOKEN}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        },
        data: updatedBooking,
    });

    expect(resp.status()).toBe(200);
    const body = await resp.json();

    expect(body.name).toBe(updatedBooking.name);
    });

    test ('Удаление пассажира', async ({ request }) => {
    const resp = await request.delete(`${baseURL}/passengers/${passenger_id}`, {
        headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': '*/*'
        }
    });

    expect(resp.status()).toBe(204);
});
});
