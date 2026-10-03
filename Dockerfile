FROM python:3.13-slim
WORKDIR /app
COPY contract_diff_analyzer ./contract_diff_analyzer
RUN useradd --uid 10001 --create-home runner
USER runner
WORKDIR /workspace
ENV PYTHONPATH=/app PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "contract_diff_analyzer"]
CMD ["--help"]
