import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Configuración básica Swagger
  const config = new DocumentBuilder()
    .setTitle('API de Reservas de Salas')
    .setDescription('API REST para gestionar reservas en un restaurante')
    .setVersion('1.0')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document); // La documentación estará en /api

  await app.listen(3000);
}
bootstrap();
